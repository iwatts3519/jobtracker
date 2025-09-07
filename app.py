from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobtracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

from models import db, Job, User, Application, Company
from services.ai_service import ai_service
from services.job_scraper import job_scraper
from services.cv_processor import cv_processor

db.init_app(app)

@app.route('/')
def index():
    jobs = Job.query.all()
    saved_jobs = Job.query.filter_by(status='saved').all()
    applied_jobs = Job.query.filter_by(status='applied').all()
    interview_jobs = Job.query.filter_by(status='interview').all()
    offered_jobs = Job.query.filter_by(status='offered').all()
    
    return render_template('index.html', 
                         saved_jobs=saved_jobs,
                         applied_jobs=applied_jobs,
                         interview_jobs=interview_jobs,
                         offered_jobs=offered_jobs)

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        url = request.form['url']
        title = request.form.get('title', '')
        company = request.form.get('company', '')
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        
        job = Job(
            url=url,
            title=title,
            company=company,
            description=description,
            location=location,
            status='saved',
            date_added=datetime.utcnow()
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('job_form.html')

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@app.route('/update_job_status', methods=['POST'])
def update_job_status():
    job_id = request.json['job_id']
    new_status = request.json['status']
    
    job = Job.query.get_or_404(job_id)
    job.status = new_status
    
    if new_status == 'applied' and not job.date_applied:
        job.date_applied = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/scrape_job_url', methods=['POST'])
def scrape_job_url():
    """Auto-fill job details by scraping the provided URL"""
    url = request.json.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    try:
        job_info = job_scraper.extract_job_info(url)
        return jsonify({'success': True, 'job_info': job_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cv_customizer')
def cv_customizer():
    """CV customization interface"""
    return render_template('cv_customizer.html', ai_available=ai_service.is_available())

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    """Handle CV file upload"""
    if 'cv_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('cv_customizer'))
    
    file = request.files['cv_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('cv_customizer'))
    
    result = cv_processor.save_uploaded_file(file)
    if result is None:
        flash('Failed to upload CV. Please check file type and size.', 'error')
        return redirect(url_for('cv_customizer'))
    
    filepath, extracted_text = result
    
    # For now, we'll just return the extracted text
    # In a full app, you'd save this to the user's profile
    flash('CV uploaded successfully!', 'success')
    return render_template('cv_customizer.html', 
                         ai_available=ai_service.is_available(),
                         cv_text=extracted_text,
                         cv_path=filepath)

@app.route('/customize_cv/<int:job_id>', methods=['POST'])
def customize_cv(job_id):
    """Customize CV for a specific job"""
    job = Job.query.get_or_404(job_id)
    cv_text = request.form.get('cv_text', '')
    
    if not cv_text:
        flash('No CV content provided', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    if not ai_service.is_available():
        flash('AI service not available. Please configure OpenAI API key.', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    try:
        customized_cv = ai_service.customize_cv(
            cv_text=cv_text,
            job_description=job.description or '',
            job_title=job.title or '',
            company=job.company or ''
        )
        
        if customized_cv:
            # Save the customized CV
            cv_path = cv_processor.save_customized_cv(customized_cv, job_id)
            flash('CV customized successfully!', 'success')
            
            return render_template('customized_cv.html', 
                                 job=job, 
                                 customized_cv=customized_cv,
                                 cv_path=cv_path)
        else:
            flash('Failed to customize CV. Please try again.', 'error')
            return redirect(url_for('job_detail', job_id=job_id))
            
    except Exception as e:
        flash(f'CV customization failed: {str(e)}', 'error')
        return redirect(url_for('job_detail', job_id=job_id))

@app.route('/generate_cover_letter/<int:job_id>', methods=['POST'])
def generate_cover_letter(job_id):
    """Generate cover letter for a specific job"""
    job = Job.query.get_or_404(job_id)
    cv_text = request.form.get('cv_text', '')
    user_name = request.form.get('user_name', '')
    
    if not cv_text:
        flash('No CV content provided', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    if not ai_service.is_available():
        flash('AI service not available. Please configure OpenAI API key.', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    try:
        cover_letter = ai_service.generate_cover_letter(
            cv_text=cv_text,
            job_description=job.description or '',
            job_title=job.title or '',
            company=job.company or '',
            user_name=user_name
        )
        
        if cover_letter:
            # Save the cover letter
            letter_path = cv_processor.save_cover_letter(cover_letter, job_id)
            flash('Cover letter generated successfully!', 'success')
            
            return render_template('cover_letter.html', 
                                 job=job, 
                                 cover_letter=cover_letter,
                                 letter_path=letter_path)
        else:
            flash('Failed to generate cover letter. Please try again.', 'error')
            return redirect(url_for('job_detail', job_id=job_id))
            
    except Exception as e:
        flash(f'Cover letter generation failed: {str(e)}', 'error')
        return redirect(url_for('job_detail', job_id=job_id))

@app.route('/research_company/<int:job_id>')
def research_company(job_id):
    """Research company for a specific job"""
    job = Job.query.get_or_404(job_id)
    
    if not job.company:
        flash('No company name available for research', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    if not ai_service.is_available():
        flash('AI service not available. Please configure OpenAI API key.', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    try:
        research_data = ai_service.research_company(
            company_name=job.company,
            job_title=job.title or ''
        )
        
        if research_data:
            return render_template('company_research.html', 
                                 job=job, 
                                 research=research_data)
        else:
            flash('Failed to research company. Please try again.', 'error')
            return redirect(url_for('job_detail', job_id=job_id))
            
    except Exception as e:
        flash(f'Company research failed: {str(e)}', 'error')
        return redirect(url_for('job_detail', job_id=job_id))

@app.route('/job_search')
def job_search():
    """Job search interface using JobSpy"""
    return render_template('job_search.html')

@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    """Search for jobs using JobSpy"""
    search_term = request.form.get('search_term', '')
    location = request.form.get('location', '')
    site = request.form.get('site', 'indeed')
    results_wanted = int(request.form.get('results_wanted', 10))
    
    if not search_term:
        flash('Please enter a search term', 'error')
        return redirect(url_for('job_search'))
    
    try:
        jobs = job_scraper.scrape_with_jobspy(
            site=site,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted
        )
        
        if jobs is None:
            flash('Job scraping service not available', 'error')
            return redirect(url_for('job_search'))
        elif len(jobs) == 0:
            flash('No jobs found for your search criteria', 'warning')
            return redirect(url_for('job_search'))
        else:
            return render_template('search_results.html', 
                                 jobs=jobs, 
                                 search_term=search_term,
                                 location=location)
            
    except Exception as e:
        flash(f'Job search failed: {str(e)}', 'error')
        return redirect(url_for('job_search'))

@app.route('/save_scraped_job', methods=['POST'])
def save_scraped_job():
    """Save a job from search results"""
    job_data = request.json
    
    job = Job(
        url=job_data.get('url', ''),
        title=job_data.get('title', ''),
        company=job_data.get('company', ''),
        description=job_data.get('description', ''),
        location=job_data.get('location', ''),
        salary_range=job_data.get('salary', ''),
        status='saved',
        date_added=datetime.utcnow()
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({'success': True, 'job_id': job.id})

@app.route('/get_cv_list', methods=['GET'])
def get_cv_list():
    """Get list of uploaded CVs for selection"""
    cv_files = cv_processor.list_uploaded_cvs()
    return jsonify({'success': True, 'cvs': cv_files})

@app.route('/get_cv_text/<filename>', methods=['GET'])
def get_cv_text(filename):
    """Get CV text content by filename"""
    cv_text = cv_processor.get_cv_text_by_filename(filename)
    if cv_text:
        return jsonify({'success': True, 'cv_text': cv_text})
    else:
        return jsonify({'success': False, 'error': 'Could not extract CV text'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        os.makedirs('static/uploads', exist_ok=True)
    
    app.run(debug=True)