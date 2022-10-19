from flask import Blueprint, render_template, request
import concurrent.futures
from . import license_query


license_status = Blueprint('license_status', __name__)

@license_status.route('/license_status', methods=['GET'])
def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        software1 = executor.submit(license_query.license_status, 'software1')
        software2 = executor.submit(license_query.license_status, 'software2')
        
        software1 = software1.result()
        software2 = software2.result()

    return render_template('license_status.html', software1=software1, software2=software2)