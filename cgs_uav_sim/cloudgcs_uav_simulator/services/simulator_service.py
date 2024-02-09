import frappe
from cloud_base_app.cloud_base_app.services.service_base import ServiceBase
from .file_utils import get_file_content_base64

class SimulatorService(ServiceBase):
    def __init__(self):
        settings = frappe.get_doc('Simulator Settings')
        super().__init__('SimulatorService', 'CloudGCS UAV Simulator',settings.base_url) 

    def kill_mission_controller(self, aircraft_name: str):
        response = self.delete(f"process/{aircraft_name}/mission-controller")
        return response.ok

    def kill_auto_pilot(self, aircraft_name: str):
        response = self.delete(f"process/{aircraft_name}/autopilot")
        return response.ok

    def start_mission_controller(self, aircraft_name: str):
        response = self.post(f"process/{aircraft_name}/mission-controller")
        return response.ok

    def start_auto_pilot(self, aircraft_name: str):
        response = self.post(f"process/{aircraft_name}/autopilot")
        return response.ok

    def get_certificates(self):
        settings = frappe.get_doc('Tenant Settings')
        tenant_name = settings.tenant_code
        response = self.get(f"certificate?tenantName={tenant_name}")
        if response.ok: return response.json()
        return None

    def update_certificates(self, aircraft_doc):
        #todo: put method handler does something completely different
        #response = self.put(f"certificate", param)
        #return response.ok
        return self.create_certificate(aircraft_doc, False)

    def create_certificate(self, aircraft_doc, is_new: bool = True):
        file_content = get_file_content_base64(aircraft_doc.certificate)
        if file_content is None: return None
        data = {
        	"name": aircraft_doc.name,
        	"files": [
        		{
        			"base64": file_content,
        			"fileName": "client.pfx"
        		}
        	],
    	    "isReNew": not is_new
        }
        response = self.post(f"certificate", data)
        return response.ok

    def soft_reset_configs(self, aircraft_name: str):
        response = self.delete(f"config/{param}/soft-delete")
        return response.ok

    def hard_reset_configs(self, aircraft_name: str):
        response = self.delete(f"config/{param}/hard-delete")
        return response.ok

    def save_as_default(self, aircraft_name: str):
        response = self.post(f"config/{aircraft_name}/save-as-default")
        return response.ok

    def is_soft_reset_available(self, aircraft_name: str):
        response = self.get(f"config/{aircraft_name}/default-configs")
        return response.ok

    def fetch_check_boxes(self, aircraft_name: str):
        response = self.get(f"aircraft/{aircraft_name}/settings")
        if response.ok: return response.json()
        return None

    def post_settings(self, sim_doc):
        aircraft_name = sim_doc.aircraft
        # Prepare payload
        device_dict = {
            "airspeed_a": "AirspeedA",
            "airspeed_b": "AirspeedB",
            "gps": "GPS",
            "main_engine": "MainEngine",
            "vtol_feedback": "VTOLFeedback",
            "vtol_motor": "VTOLMotor",
            "datalink_a": "DatalinkA",
            "datalink_b": "DatalinkB",
            "datalink_a_delay": "DatalinkADelay",
            "datalink_b_delay": "DatalinkBDelay"
        }

        devices = []
        for key in device_dict.keys():
            if getattr(sim_doc, key, False) == True:
                devices.append(device_dict[key])
                
        data = {
            "devices": devices,
            "weatherSettings": {
                "windSpeed": sim_doc.wind_speed,
                "windDirection": sim_doc.wind_direction,
                "gustIntensity": sim_doc.gust_intensity,
                "gustDuration": sim_doc.gust_duration,
                "gustFrequency": sim_doc.gust_frequency,
                "referenceAltitude": sim_doc.reference_altitude,
                "pressure": sim_doc.pressure,
                "temperature": sim_doc.temperature,
                "relativeHumidity": sim_doc.relative_humidity
            },
            "platformSettings": {
                "latitude": sim_doc.latitude,
                "longitude": sim_doc.longitude,
                "altitude": sim_doc.altitude,
                "speed": sim_doc.speed,
                "direction": sim_doc.direction
            }
        }
        response = self.put(f"aircraft/{aircraft_name}/settings", data)
        return response.ok

    def restart(self):
        response = self.delete(f"aircraft/clear")
        return response.ok

    def reset_aircraft(self, aircraft_name: str):
        response = self.delete(f"aircraft/{aircraft_name}/reset")
        return response.ok

    def get_aircrafts(self):
        response = self.get(f"aircraft")
        if response.ok:
            return response.json()
        return None
        
    def start_simulation(self, simulation_name: str):
        sim_doc = frappe.get_doc("Simulation", simulation_name)
        if sim_doc.is_active: return True

        #check if we can actually start simulation before making the call
        sim_doc.is_active = True
        sim_doc.validate()
        
        data = {
            "aircraftType": sim_doc.aircraft_type,
            "name": sim_doc.aircraft,
            "payloadWeight": sim_doc.payload_weight,
            "fuelWeight": sim_doc.fuel_weight,
            "latitude": sim_doc.latitude,
            "longitude": sim_doc.longitude,
            "altitude": sim_doc.altitude,
            "roll": sim_doc.roll,
            "pitch": sim_doc.pitch,
            "yaw": sim_doc.direction,
            "speed": sim_doc.speed,
            "aircraftStatus": sim_doc.aircraft_status,
            
            "isTest": False,
            "userId": -1,
            "startConfig": {},
            "selectedAutoPilot": 0
        }
        response = self.post(f"aircraft", data)
        sim_doc.save()
        return response.ok

    def stop_simulation(self, simulation_name: str):
        sim_doc = frappe.get_doc("Simulation", simulation_name)
        if not sim_doc.is_active: return True
        aircraft_name = sim_doc.aircraft
        response = self.post(f"aircraft/{aircraft_name}/stop")
        sim_doc.is_active = False
        sim_doc.save()
        return response.ok

    def launch_aircraft(self, aircraft_name: str):
        response = self.post(f"aircraft/{aircraft_name}/launch")
        return response.ok
