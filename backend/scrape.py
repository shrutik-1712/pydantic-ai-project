import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import requests
from selenium.common.exceptions import TimeoutException

def scrape_portfolio(url):
    """
    Scrape portfolio data from the given URL using Selenium and BeautifulSoup
    with enhanced waiting and element selection
    """
    print(f"Starting to scrape {url}")
    
    # Set up headless Chrome with additional options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1920, 1080)  # Set a realistic window size
    
    try:
        # Load the page
        driver.get(url)
        
        # Wait for key elements to load (more reliable than sleep)
        print("Waiting for page to load completely...")
        try:
            # Wait for specific elements that indicate page is loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            print("Main content loaded")
        except TimeoutException:
            print("Timeout waiting for main content, continuing anyway")
        
        # Give extra time for any animations or delayed content
        time.sleep(3)
        
        # Get the page source after JavaScript has rendered
        page_source = driver.page_source
        
        # Save HTML for debugging
        with open('portfolio_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Saved raw HTML to portfolio_page.html for inspection")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract portfolio data using both direct DOM and JavaScript state approaches
        portfolio_data = {
            "owner": extract_owner_info(soup, driver),
            "about": extract_about_section(soup, driver),
            "skills": extract_skills(soup, driver),
            "projects": extract_projects(soup, driver),
            "experience": extract_experience(soup, driver),
            "education": extract_education(soup, driver),
            "contact": extract_contact_info(soup, driver)
        }
        
        # Try to extract data directly from any global variables the site might expose
        try:
            # Get any potential React or Next.js data states
            app_data = driver.execute_script("""
                // Try different ways Next.js/React might store data
                const dataFromProps = window.__NEXT_DATA__ ? window.__NEXT_DATA__.props.pageProps : null;
                const dataFromState = window.__STATE__ || null;
                return { fromProps: dataFromProps, fromState: dataFromState };
            """)
            
            if app_data and (app_data.get('fromProps') or app_data.get('fromState')):
                portfolio_data["app_data"] = app_data
                print("Found application state data through JavaScript")
        except Exception as e:
            print(f"Error extracting JavaScript state data: {e}")
            
        # Save data to JSON file
        with open('portfolio_data.json', 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        print("Scraping completed. Data saved to portfolio_data.json")
        return portfolio_data
        
    finally:
        # Take a screenshot for debugging
        driver.save_screenshot('portfolio_screenshot.png')
        print("Saved screenshot to portfolio_screenshot.png")
        driver.quit()

def extract_owner_info(soup, driver):
    """Extract owner/personal info from the page using both BeautifulSoup and JavaScript execution"""
    owner_info = {}
    
    try:
        # Use JavaScript to get text content directly
        name = driver.execute_script("""
            const nameElem = document.querySelector('h1') || document.querySelector('.hero-name');
            return nameElem ? nameElem.textContent : '';
        """)
        if name:
            owner_info['name'] = name.strip()
            
        title = driver.execute_script("""
            const titleElem = document.querySelector('h2') || document.querySelector('.hero-title');
            return titleElem ? titleElem.textContent : '';
        """)
        if title:
            owner_info['title'] = title.strip()
            
        # Try different selectors for finding the bio content
        selectors = ['p.hero-text', 'div.hero-content p', '.intro p', '.about-content p']
        for selector in selectors:
            try:
                bio_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if bio_elements:
                    owner_info['bio'] = ' '.join([el.text.strip() for el in bio_elements])
                    break
            except:
                continue
    except Exception as e:
        print(f"Error extracting owner info via JavaScript: {e}")
    
    # Fallback to BeautifulSoup if JavaScript approach didn't work
    if not owner_info.get('name'):
        # Try various possible selectors for the name
        for selector in ['h1', '.hero-name', '.name', '.title-name']:
            name_element = soup.select_one(selector)
            if name_element and name_element.text.strip():
                owner_info['name'] = name_element.text.strip()
                break
    
    if not owner_info.get('title'):
        # Try various possible selectors for the title/role
        for selector in ['h2', '.hero-title', '.subtitle', '.profession']:
            title_element = soup.select_one(selector)
            if title_element and title_element.text.strip():
                owner_info['title'] = title_element.text.strip()
                break
    
    # Print all headings for debugging
    print("Debugging - All heading elements:")
    headings = soup.find_all(['h1', 'h2', 'h3'])
    for h in headings[:10]:  # Limit to first 10 to avoid overwhelming output
        print(f"{h.name}: {h.text.strip()}")
    
    return owner_info

def extract_about_section(soup, driver):
    """Extract about section content"""
    about_data = {}
    
    try:
        # Try to get about content using JavaScript
        about_text = driver.execute_script("""
            const aboutSection = document.getElementById('about') || document.querySelector('.about-section');
            if (!aboutSection) return '';
            
            const paragraphs = aboutSection.querySelectorAll('p');
            return Array.from(paragraphs).map(p => p.textContent.trim()).join(' ');
        """)
        
        if about_text:
            about_data['description'] = about_text
    except Exception as e:
        print(f"Error extracting about section via JavaScript: {e}")
    
    # Fallback to BeautifulSoup
    if not about_data.get('description'):
        about_selectors = ['#about', '.about-section', '.about', 'section.about']
        for selector in about_selectors:
            about_section = soup.select_one(selector)
            if about_section:
                paragraphs = about_section.select('p')
                if paragraphs:
                    about_data['description'] = ' '.join([p.text.strip() for p in paragraphs])
                    break
    
    return about_data

def extract_skills(soup, driver):
    """Extract skills section using a more flexible approach"""
    skills_list = []
    
    try:
        # Use JavaScript to find skills
        skills_script = """
            const skillsSection = document.getElementById('skills') || 
                                document.querySelector('.skills-section') || 
                                document.querySelector('section.skills');
            if (!skillsSection) return [];
            
            // Look for different ways skills might be represented
            const skillElements = skillsSection.querySelectorAll('.skill-item, .skill-card, .skill, li');
            return Array.from(skillElements).map(el => el.textContent.trim());
        """
        skills_from_js = driver.execute_script(skills_script)
        
        if skills_from_js and len(skills_from_js) > 0:
            # Clean up the skills (remove empty strings, duplicates)
            skills_list = [skill for skill in skills_from_js if skill]
            skills_list = list(dict.fromkeys(skills_list))  # Remove duplicates while preserving order
    except Exception as e:
        print(f"Error extracting skills via JavaScript: {e}")
    
    # Fallback to BeautifulSoup if needed
    if not skills_list:
        # Try various selectors that might contain skills
        skills_selectors = ['#skills', '.skills-section', '.skills', 'section.skills']
        item_selectors = ['.skill-item', '.skill-card', '.skill', 'li', 'span.tag', '.skill-tag']
        
        for section_selector in skills_selectors:
            section = soup.select_one(section_selector)
            if not section:
                continue
                
            for item_selector in item_selectors:
                items = section.select(item_selector)
                if items:
                    # Extract text from each skill element
                    skills_list = [item.text.strip() for item in items if item.text.strip()]
                    if skills_list:
                        break
            
            if skills_list:
                break
    
    return skills_list

def extract_projects(soup, driver):
    """Extract projects section"""
    projects = []
    
    try:
        # Use JavaScript to extract project information
        js_script = """
            const projectsSection = document.getElementById('projects') || 
                                  document.querySelector('.projects-section') || 
                                  document.querySelector('section.projects');
            if (!projectsSection) return [];
            
            const projectCards = projectsSection.querySelectorAll('.project-card, .project, .card');
            return Array.from(projectCards).map(card => {
                const project = {};
                
                // Title
                const titleElem = card.querySelector('h3, h2, .title, .project-title');
                if (titleElem) project.title = titleElem.textContent.trim();
                
                // Description
                const descElem = card.querySelector('p, .description, .project-description');
                if (descElem) project.description = descElem.textContent.trim();
                
                // Links
                const links = card.querySelectorAll('a');
                Array.from(links).forEach(link => {
                    const href = link.href || '';
                    if (href.includes('github')) {
                        project.github_url = href;
                    } else if (link.textContent.toLowerCase().includes('live') || 
                              link.textContent.toLowerCase().includes('demo') ||
                              href.includes('vercel') ||
                              href.includes('netlify')) {
                        project.live_url = href;
                    }
                });
                
                // Technologies
                const techElements = card.querySelectorAll('.tech-stack span, .technologies span, .tags span, .tag');
                if (techElements.length > 0) {
                    project.technologies = Array.from(techElements).map(tech => tech.textContent.trim());
                }
                
                return project;
            });
        """
        
        projects_from_js = driver.execute_script(js_script)
        if projects_from_js and len(projects_from_js) > 0:
            projects = [p for p in projects_from_js if p.get('title')]  # Filter out empty projects
    except Exception as e:
        print(f"Error extracting projects via JavaScript: {e}")
    
    # Fallback to BeautifulSoup if needed
    if not projects:
        # Try to find the projects section
        projects_selectors = ['#projects', '.projects-section', '.projects', 'section.projects']
        card_selectors = ['.project-card', '.project', '.card']
        
        for section_selector in projects_selectors:
            section = soup.select_one(section_selector)
            if not section:
                continue
                
            for card_selector in card_selectors:
                cards = section.select(card_selector)
                if not cards:
                    continue
                    
                for card in cards:
                    project = {}
                    
                    # Title
                    title_selectors = ['h3', 'h2', '.title', '.project-title']
                    for selector in title_selectors:
                        title_elem = card.select_one(selector)
                        if title_elem and title_elem.text.strip():
                            project['title'] = title_elem.text.strip()
                            break
                    
                    # Description
                    desc_selectors = ['p', '.description', '.project-description']
                    for selector in desc_selectors:
                        desc_elem = card.select_one(selector)
                        if desc_elem and desc_elem.text.strip():
                            project['description'] = desc_elem.text.strip()
                            break
                    
                    # Links
                    links = card.select('a')
                    for link in links:
                        href = link.get('href', '')
                        if 'github' in href.lower():
                            project['github_url'] = href
                        elif ('live' in link.text.lower() or 'demo' in link.text.lower() or 
                             'vercel' in href.lower() or 'netlify' in href.lower()):
                            project['live_url'] = href
                    
                    # Technologies
                    tech_selectors = ['.tech-stack span', '.technologies span', '.tags span', '.tag']
                    for selector in tech_selectors:
                        tech_elems = card.select(selector)
                        if tech_elems:
                            project['technologies'] = [tech.text.strip() for tech in tech_elems if tech.text.strip()]
                            break
                    
                    if project.get('title'):  # Only add if we found a title
                        projects.append(project)
                
                if projects:  # If we found projects with this card selector, stop looking
                    break
            
            if projects:  # If we found projects in this section, stop looking
                break
    
    return projects

def extract_experience(soup, driver):
    """Extract professional experience"""
    experiences = []
    
    try:
        # Use JavaScript to extract experience information
        js_script = """
            const expSection = document.getElementById('experience') || 
                             document.querySelector('.experience-section') || 
                             document.querySelector('section.experience');
            if (!expSection) return [];
            
            const expItems = expSection.querySelectorAll('.experience-item, .job, .position, .work-item');
            return Array.from(expItems).map(item => {
                const exp = {};
                
                // Title
                const titleElem = item.querySelector('h3, .title, .job-title');
                if (titleElem) exp.title = titleElem.textContent.trim();
                
                // Company
                const companyElem = item.querySelector('h4, .company, .employer');
                if (companyElem) exp.company = companyElem.textContent.trim();
                
                // Date range
                const dateElem = item.querySelector('.date, .duration, .period');
                if (dateElem) exp.date_range = dateElem.textContent.trim();
                
                // Responsibilities
                const respElems = item.querySelectorAll('li, p.description');
                if (respElems.length > 0) {
                    exp.responsibilities = Array.from(respElems).map(el => el.textContent.trim());
                }
                
                return exp;
            });
        """
        
        exp_from_js = driver.execute_script(js_script)
        if exp_from_js and len(exp_from_js) > 0:
            experiences = [e for e in exp_from_js if e.get('title') or e.get('company')]  # Filter out empty entries
    except Exception as e:
        print(f"Error extracting experience via JavaScript: {e}")
    
    # Fallback using BeautifulSoup similar to projects function
    # ... (similar implementation to the projects function, adapted for experience)
    
    return experiences

def extract_education(soup, driver):
    """Extract education information"""
    education = []
    
    try:
        # Use JavaScript to extract education information
        js_script = """
            const eduSection = document.getElementById('education') || 
                             document.querySelector('.education-section') || 
                             document.querySelector('section.education');
            if (!eduSection) return [];
            
            const eduItems = eduSection.querySelectorAll('.education-item, .degree, .school-item');
            return Array.from(eduItems).map(item => {
                const edu = {};
                
                // Degree
                const degreeElem = item.querySelector('h3, .degree, .qualification');
                if (degreeElem) edu.degree = degreeElem.textContent.trim();
                
                // Institution
                const instElem = item.querySelector('h4, .institution, .school, .university');
                if (instElem) edu.institution = instElem.textContent.trim();
                
                // Date range
                const dateElem = item.querySelector('.date, .duration, .period');
                if (dateElem) edu.date_range = dateElem.textContent.trim();
                
                // Description
                const descElem = item.querySelector('p.description, .details');
                if (descElem) edu.description = descElem.textContent.trim();
                
                return edu;
            });
        """
        
        edu_from_js = driver.execute_script(js_script)
        if edu_from_js and len(edu_from_js) > 0:
            education = [e for e in edu_from_js if e.get('degree') or e.get('institution')]  # Filter out empty entries
    except Exception as e:
        print(f"Error extracting education via JavaScript: {e}")
    
    # Fallback using BeautifulSoup similar to projects function
    # ... (similar implementation to the projects function, adapted for education)
    
    return education

def extract_contact_info(soup, driver):
    """Extract contact information"""
    contact_info = {}
    
    try:
        # Try to extract contact info using JavaScript
        js_script = """
            const contactSection = document.getElementById('contact') || 
                                 document.querySelector('.contact-section') || 
                                 document.querySelector('section.contact');
            if (!contactSection) return {};
            
            const result = {};
            
            // Email
            const emailLink = contactSection.querySelector('a[href^="mailto:"]');
            if (emailLink) {
                result.email = emailLink.href.replace('mailto:', '');
            }
            
            // Social links
            const socialLinks = {};
            const links = contactSection.querySelectorAll('a');
            Array.from(links).forEach(link => {
                const href = link.href || '';
                if (href.includes('github.com')) {
                    socialLinks.github = href;
                } else if (href.includes('linkedin.com')) {
                    socialLinks.linkedin = href;
                } else if (href.includes('twitter.com')) {
                    socialLinks.twitter = href;
                }
            });
            
            if (Object.keys(socialLinks).length > 0) {
                result.social = socialLinks;
            }
            
            return result;
        """
        
        contact_from_js = driver.execute_script(js_script)
        if contact_from_js:
            contact_info = contact_from_js
    except Exception as e:
        print(f"Error extracting contact info via JavaScript: {e}")
    
    # Fallback to BeautifulSoup if needed
    if not contact_info:
        contact_selectors = ['#contact', '.contact-section', '.contact', 'section.contact', 'footer']
        
        for selector in contact_selectors:
            section = soup.select_one(selector)
            if not section:
                continue
            
            # Email
            email_link = section.select_one('a[href^="mailto:"]')
            if email_link:
                contact_info['email'] = email_link.get('href').replace('mailto:', '')
            
            # Social links
            social_links = {}
            links = section.select('a')
            
            for link in links:
                href = link.get('href', '')
                if 'github.com' in href:
                    social_links['github'] = href
                elif 'linkedin.com' in href:
                    social_links['linkedin'] = href
                elif 'twitter.com' in href:
                    social_links['twitter'] = href
            
            if social_links:
                contact_info['social'] = social_links
            
            if contact_info:  # If we found any contact info, stop looking
                break
    
    return contact_info

def try_puppeteer_approach(url):
    """
    This is a conceptual function showing how you might use Puppeteer with Node.js
    You would need to create a separate JS file and call it from Python
    """
    import subprocess
    import os
    
    # Create a temporary puppeteer script
    with open('puppeteer_scraper.js', 'w') as f:
        f.write("""
        const puppeteer = require('puppeteer');

        (async () => {
          const browser = await puppeteer.launch();
          const page = await browser.newPage();
          await page.goto('""" + url + """', {waitUntil: 'networkidle2'});
          
          // Wait for content to load
          await page.waitForSelector('main', {timeout: 5000}).catch(() => console.log('Main element not found'));
          
          // Extract data
          const data = await page.evaluate(() => {
            // Similar extraction logic to what we used in Selenium
            // ...
            
            return {
              title: document.title,
              content: document.body.innerText
              // Add more structured extraction here
            };
          });
          
          console.log(JSON.stringify(data));
          await browser.close();
        })();
        """)
    
    # This is conceptual - you would need Node.js and puppeteer installed
    # result = subprocess.run(['node', 'puppeteer_scraper.js'], capture_output=True, text=True)
    # return json.loads(result.stdout)
    
    return {"note": "This is a conceptual function - actual implementation would require Node.js and puppeteer"}

if __name__ == "__main__":
    portfolio_url = "https://portfolio-jytw.vercel.app/"
    portfolio_data = scrape_portfolio(portfolio_url)
    print("Portfolio data structure:")
    print(json.dumps(portfolio_data, indent=2))
    
    # Uncomment to try alternative approach if the above doesn't work
    # print("\nTrying alternative approach with different technique...")
    # try:
    #     # Try a different approach - this is conceptual and would need implementation
    #     # puppeteer_data = try_puppeteer_approach(portfolio_url)
    #     # print(json.dumps(puppeteer_data, indent=2))
    # except Exception as e:
    #     print(f"Alternative approach failed: {e}")