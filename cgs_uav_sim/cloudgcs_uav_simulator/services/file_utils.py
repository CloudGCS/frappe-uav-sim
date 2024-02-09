import frappe
import base64

def get_file_content_base64(file_url):
    if file_url:
        file_doc = frappe.get_doc("File", {"file_url": file_url})
        file_path = file_doc.get_full_path()
        if not file_path: return None
        with open(file_path, 'rb') as file:
            content = file.read()
            encoded_content = base64.b64encode(content)
            return encoded_content.decode('utf-8')

    return None
