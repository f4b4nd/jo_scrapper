class Alert:
    
    def __init__(self, filename):
        self.filename = filename
        
    def run(self, status):
        alerts = {
            "success": f"# File {self.filename} created !",
            "already_exists": f"# File {self.filename} already exists",
            "no_data": f"No data on {self.filename}",
        }
        status = alerts[status] if status in alerts else ""
        print(status)
