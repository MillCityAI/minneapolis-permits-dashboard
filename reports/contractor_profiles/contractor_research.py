#!/usr/bin/env python3
"""
Contractor Research Script
Gathers additional information about plumbing contractors from web sources
"""

import json
import pandas as pd
import os
from datetime import datetime
import re
from typing import Dict, List, Optional
import time


class ContractorResearcher:
    def __init__(self, contractor_csv_path: str):
        """Initialize the researcher with contractor data"""
        self.contractors_df = pd.read_csv(contractor_csv_path)
        self.template_path = "contractor_data_template.json"
        self.output_dir = "contractor_profiles"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load the JSON template
        with open(self.template_path, 'r') as f:
            self.template = json.load(f)
    
    def clean_company_name(self, name: str) -> str:
        """Clean company name for file naming"""
        # Remove special characters and spaces
        clean_name = re.sub(r'[^\w\s-]', '', name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        return clean_name.lower()
    
    def extract_existing_data(self, contractor_row) -> Dict:
        """Extract data we already have from the CSV"""
        data = json.loads(json.dumps(self.template))  # Deep copy template
        
        # Company info
        data['company_info']['company_name'] = contractor_row['Company_Name']
        data['company_info']['legal_name'] = contractor_row.get('Matched_License_Company', contractor_row['Company_Name'])
        
        # Contact info
        data['contact_info']['primary_contact']['name'] = contractor_row.get('Contact_Person', '')
        data['contact_info']['main_phone'] = contractor_row.get('Phone_Number', '')
        data['contact_info']['emails']['general'] = contractor_row.get('Email', '')
        
        # Location info
        data['location_info']['primary_address']['street'] = contractor_row.get('Address', '')
        data['location_info']['primary_address']['city'] = contractor_row.get('City', '')
        data['location_info']['service_areas'] = contractor_row.get('Service_Areas', '').split(', ') if contractor_row.get('Service_Areas') else []
        
        # Performance metrics
        data['performance_metrics']['permit_data']['total_permits'] = int(contractor_row.get('Total_Permits', 0))
        data['performance_metrics']['permit_data']['avg_permits_per_year'] = float(contractor_row.get('Avg_Permits_Per_Year', 0))
        data['performance_metrics']['permit_data']['first_permit_date'] = contractor_row.get('First_Permit_Date', '')
        data['performance_metrics']['permit_data']['last_permit_date'] = contractor_row.get('Last_Permit_Date', '')
        data['performance_metrics']['permit_data']['days_since_last_permit'] = int(contractor_row.get('Days_Since_Last_Permit', 0))
        data['performance_metrics']['permit_data']['total_fees_paid'] = float(contractor_row.get('Total_Fees_Paid', 0))
        data['performance_metrics']['permit_data']['activity_level'] = contractor_row.get('Activity_Level', '')
        
        # Parse top work types
        work_types = contractor_row.get('Top_Work_Types', '')
        if work_types:
            data['performance_metrics']['permit_data']['top_work_types'] = [
                wt.strip() for wt in work_types.split(',')
            ]
        
        # Metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['data_source'] = contractor_row.get('Contact_Info_Source', 'Minneapolis Permits Database')
        data['metadata']['verification_status'] = contractor_row.get('Contact_Confidence', 'Unverified')
        
        return data
    
    def format_phone_for_search(self, phone: str) -> str:
        """Format phone number for web searches"""
        # Remove all non-numeric characters
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        return phone
    
    def research_contractor_web(self, contractor_data: Dict) -> Dict:
        """
        Perform web research to gather additional contractor information
        This is a placeholder for actual web research functionality
        """
        company_name = contractor_data['company_info']['company_name']
        city = contractor_data['location_info']['primary_address']['city']
        phone = contractor_data['contact_info']['main_phone']
        
        # Format search queries
        search_queries = {
            'business_info': f'"{company_name}" plumbing {city} Minnesota business information',
            'reviews': f'"{company_name}" plumbing reviews ratings {city}',
            'website': f'"{company_name}" plumbing {phone} website',
            'bbb': f'"{company_name}" better business bureau BBB rating',
            'social_media': f'"{company_name}" plumbing facebook linkedin',
            'news': f'"{company_name}" plumbing news announcements {city}'
        }
        
        # Add placeholder for web research results
        contractor_data['web_research']['research_notes'].append({
            'timestamp': datetime.now().isoformat(),
            'action': 'Web research queries prepared',
            'queries': search_queries
        })
        
        # In a real implementation, this would perform actual web searches
        # For now, we'll add some example data structure
        contractor_data['marketing_intelligence']['unique_selling_points'] = [
            "Licensed and insured",
            "24/7 emergency service",
            "Family-owned business",
            "Serving Minneapolis area"
        ]
        
        contractor_data['business_details']['specialties'] = [
            "Residential plumbing",
            "Commercial plumbing",
            "Water heater installation",
            "Drain cleaning"
        ]
        
        return contractor_data
    
    def create_contractor_html(self, contractor_data: Dict) -> str:
        """Generate HTML page for a contractor using the template"""
        # Read the HTML template
        template_html_path = os.path.join(os.path.dirname(self.output_dir), "contractor_detail_template.html")
        with open(template_html_path, 'r') as f:
            html_template = f.read()
        
        # Format values for display
        def format_currency(value):
            try:
                return f"{float(value):,.0f}"
            except:
                return "0"
        
        def format_list(items):
            if isinstance(items, list):
                return ", ".join(str(item) for item in items if item)
            return str(items)
        
        # Replace placeholders with actual data
        replacements = {
            '{COMPANY_NAME}': contractor_data['company_info']['company_name'],
            '{LAST_UPDATED}': datetime.fromisoformat(contractor_data['metadata']['last_updated']).strftime('%B %d, %Y %I:%M %p'),
            '{CONTACT_PERSON}': contractor_data['contact_info']['primary_contact']['name'] or 'Not Available',
            '{PHONE_NUMBER}': contractor_data['contact_info']['main_phone'] or 'Not Available',
            '{EMAIL}': contractor_data['contact_info']['emails']['general'] or 'Not Available',
            '{ADDRESS}': contractor_data['location_info']['primary_address']['street'] or 'Not Available',
            '{CITY}': contractor_data['location_info']['primary_address']['city'] or 'Not Available',
            '{WEBSITE}': contractor_data['contact_info']['website'] or '#',
            '{WEBSITE_DISPLAY}': contractor_data['contact_info']['website'] or 'Not Available',
            '{TOTAL_PERMITS}': str(contractor_data['performance_metrics']['permit_data']['total_permits']),
            '{AVG_PERMITS_YEAR}': f"{contractor_data['performance_metrics']['permit_data']['avg_permits_per_year']:.1f}",
            '{DAYS_SINCE_LAST}': str(contractor_data['performance_metrics']['permit_data']['days_since_last_permit']),
            '{TOTAL_FEES}': format_currency(contractor_data['performance_metrics']['permit_data']['total_fees_paid']),
            '{LEGAL_NAME}': contractor_data['company_info']['legal_name'] or contractor_data['company_info']['company_name'],
            '{BUSINESS_TYPE}': contractor_data['company_info']['business_type'] or 'Not Available',
            '{LICENSE_NUMBER}': contractor_data['company_info']['license_number'] or 'Not Available',
            '{YEARS_IN_BUSINESS}': str(contractor_data['company_info']['years_in_business']) if contractor_data['company_info']['years_in_business'] else 'Not Available',
            '{EMPLOYEE_COUNT}': contractor_data['company_info']['employee_count'] or 'Not Available',
            '{BBB_RATING}': contractor_data['reputation_data']['bbb_rating'] or 'Not Available',
            '{INSURANCE_STATUS}': contractor_data['business_details']['insurance']['general_liability'] or 'Not Available',
            '{BONDING_INFO}': contractor_data['business_details']['insurance']['bonding'] or 'Not Available',
            '{SPECIALTIES}': format_list(contractor_data['business_details']['specialties']) or 'Not Available',
            '{KEY_PERSONNEL}': format_list([dm['name'] for dm in contractor_data['sales_intelligence']['decision_makers']]) or 'Not Available',
            '{TOP_WORK_TYPES}': format_list(contractor_data['performance_metrics']['permit_data']['top_work_types']) or 'Not Available',
            '{ACTIVITY_LEVEL}': contractor_data['performance_metrics']['permit_data']['activity_level'] or 'Not Available',
            '{FIRST_PERMIT_DATE}': contractor_data['performance_metrics']['permit_data']['first_permit_date'] or 'Not Available',
            '{LAST_PERMIT_DATE}': contractor_data['performance_metrics']['permit_data']['last_permit_date'] or 'Not Available',
            '{SERVICE_AREAS}': format_list(contractor_data['location_info']['service_areas']) or 'Not Available',
            '{GOOGLE_RATING}': f"{contractor_data['reputation_data']['google_rating']}/5" if contractor_data['reputation_data']['google_rating'] else 'Not Available',
            '{TOTAL_REVIEWS}': str(contractor_data['reputation_data']['google_review_count']),
            '{COMPANY_HISTORY}': contractor_data['web_research']['company_history'] or 'Research pending...',
            '{RECENT_NEWS}': format_list(contractor_data['web_research']['recent_news']) or 'No recent news found',
            '{COMPETITIVE_ADVANTAGES}': format_list(contractor_data['marketing_intelligence']['competitive_advantages']) or 'Research pending...',
            '{SOCIAL_MEDIA}': self.format_social_media_links(contractor_data['contact_info']['social_media']),
            '{REVIEWS_HTML}': self.format_reviews_html(contractor_data['reputation_data']['recent_reviews']),
            '{NOTES_HISTORY}': self.format_notes_history(contractor_data['interaction_history']['notes']),
            '{CALL_HISTORY}': self.format_call_history(contractor_data['interaction_history']['calls'])
        }
        
        # Replace all placeholders
        html_content = html_template
        for placeholder, value in replacements.items():
            html_content = html_content.replace(placeholder, str(value))
        
        return html_content
    
    def format_social_media_links(self, social_media: Dict) -> str:
        """Format social media links for display"""
        links = []
        platforms = {
            'facebook': 'Facebook',
            'linkedin': 'LinkedIn',
            'twitter': 'Twitter',
            'instagram': 'Instagram',
            'youtube': 'YouTube'
        }
        
        for platform, label in platforms.items():
            if social_media.get(platform):
                links.append(f'<a href="{social_media[platform]}" target="_blank">{label}</a>')
        
        return ' | '.join(links) if links else 'Not Available'
    
    def format_reviews_html(self, reviews: List) -> str:
        """Format reviews for HTML display"""
        if not reviews:
            return '<div class="review-item"><p>No reviews available yet.</p></div>'
        
        html_parts = []
        for review in reviews[:5]:  # Show only top 5 reviews
            html_parts.append(f'''
                <div class="review-item">
                    <div class="review-header">
                        <span class="review-rating">★★★★★ {review.get('rating', 'N/A')}/5</span>
                        <span class="review-source">{review.get('source', 'Unknown')} - {review.get('date', 'Unknown date')}</span>
                    </div>
                    <p class="review-text">"{review.get('text', 'No review text available.')}"</p>
                </div>
            ''')
        
        return ''.join(html_parts)
    
    def format_notes_history(self, notes: List) -> str:
        """Format notes history for HTML display"""
        if not notes:
            return '<div class="note-entry"><p>No notes yet. Add your first note above!</p></div>'
        
        html_parts = []
        for note in notes[-5:]:  # Show last 5 notes
            html_parts.append(f'''
                <div class="note-entry">
                    <div class="note-header">
                        <span>{note.get('date', 'Unknown date')}</span>
                        <span>{note.get('author', 'Unknown')}</span>
                    </div>
                    <p class="note-content">{note.get('content', '')}</p>
                </div>
            ''')
        
        return ''.join(reversed(html_parts))  # Show newest first
    
    def format_call_history(self, calls: List) -> str:
        """Format call history for HTML display"""
        if not calls:
            return '<div class="call-entry"><span>No calls logged yet</span></div>'
        
        html_parts = []
        for call in calls[-10:]:  # Show last 10 calls
            status_class = call.get('status', 'unknown').lower().replace(' ', '-')
            html_parts.append(f'''
                <div class="call-entry">
                    <span>{call.get('date', 'Unknown date')} - {call.get('time', '')}</span>
                    <span class="call-status {status_class}">{call.get('status', 'Unknown')}</span>
                </div>
            ''')
        
        return ''.join(reversed(html_parts))  # Show newest first
    
    def process_contractor(self, contractor_row, output_json=True, output_html=True) -> Dict:
        """Process a single contractor"""
        print(f"\nProcessing: {contractor_row['Company_Name']}")
        
        # Extract existing data
        contractor_data = self.extract_existing_data(contractor_row)
        
        # Perform web research (placeholder for now)
        contractor_data = self.research_contractor_web(contractor_data)
        
        # Generate clean filename
        clean_name = self.clean_company_name(contractor_row['Company_Name'])
        
        # Save JSON data
        if output_json:
            json_path = os.path.join(self.output_dir, f"{clean_name}_data.json")
            with open(json_path, 'w') as f:
                json.dump(contractor_data, f, indent=2)
            print(f"  - Saved JSON: {json_path}")
        
        # Generate and save HTML
        if output_html:
            html_content = self.create_contractor_html(contractor_data)
            html_path = os.path.join(self.output_dir, f"{clean_name}.html")
            with open(html_path, 'w') as f:
                f.write(html_content)
            print(f"  - Saved HTML: {html_path}")
        
        return contractor_data
    
    def process_top_contractors(self, limit=5):
        """Process the top N contractors by permit volume"""
        # Sort by total permits descending
        top_contractors = self.contractors_df.nlargest(limit, 'Total_Permits')
        
        print(f"Processing top {limit} contractors by permit volume...")
        results = []
        
        for idx, contractor in top_contractors.iterrows():
            result = self.process_contractor(contractor)
            results.append(result)
            time.sleep(0.5)  # Be respectful with any future API calls
        
        # Create an index file
        self.create_index_file(results)
        
        return results
    
    def create_index_file(self, contractors_data: List[Dict]):
        """Create an index file listing all processed contractors"""
        index_data = []
        
        for contractor in contractors_data:
            clean_name = self.clean_company_name(contractor['company_info']['company_name'])
            index_data.append({
                'company_name': contractor['company_info']['company_name'],
                'total_permits': contractor['performance_metrics']['permit_data']['total_permits'],
                'phone': contractor['contact_info']['main_phone'],
                'html_file': f"{clean_name}.html",
                'json_file': f"{clean_name}_data.json"
            })
        
        # Save index
        index_path = os.path.join(self.output_dir, "contractor_index.json")
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        print(f"\nCreated index file: {index_path}")


def main():
    """Main execution function"""
    # Path to the contractor CSV file
    csv_path = "/home/pds/millcityai/Research/plumber_contacts_with_verified_info.csv"
    
    # Create researcher instance
    researcher = ContractorResearcher(csv_path)
    
    # Process top 5 contractors
    results = researcher.process_top_contractors(limit=5)
    
    print(f"\n✅ Successfully processed {len(results)} contractors!")
    print(f"📁 Files saved in: {researcher.output_dir}/")


if __name__ == "__main__":
    main()