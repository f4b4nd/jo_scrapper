class Alert:
    
    def __init__(self, ddmmyy):
        self.ddmmyy = ddmmyy
        
    def run(self, status):
        alerts = {
            "success": f"# File {self.ddmmyy} created !",
            "already_exists": f"# File already exists for {self.ddmmyy}",
            "no_data": f"No data on {self.ddmmyy}",
        }
        status = alerts[status] if status in alerts else ""
        print(status)
