# Copyright (c) 2024, CloudGCS and contributors
# For license information, please see license.txt
import json
import frappe
from frappe.model.document import Document
from frappe import _
from cgs_uav_sim.cloudgcs_uav_simulator.services.simulator_service import SimulatorService

class Simulation(Document):
    def validate(self):
        # Check if aircraft field is set
        if self.aircraft:
            # Fetch the linked Aircraft document
            aircraft_doc = frappe.get_doc("Aircraft", self.aircraft)

            # Check if the Aircraft is a simulator aircraft
            if not aircraft_doc.is_simulator_aircraft:
                # Raise an exception if the condition is not met
                frappe.throw(_("The linked aircraft must be a simulator aircraft."), frappe.ValidationError)

        # Check if this simulation is being set to active
        if self.is_active:
            # Query for other active simulations linked to the same aircraft
            active_simulations = frappe.get_all("Simulation", 
                                                filters={"aircraft": self.aircraft, 
                                                         "is_active": 1,
                                                         "name": ["!=", self.name]})

            # If there is another active simulation, raise an exception
            if active_simulations:
                frappe.throw(_("Another simulation linked to this aircraft is already active. Only one simulation can be active at a time."), frappe.ValidationError)
        
        if self.is_active:
            service = SimulatorService()
            service.post_settings(self)

def get_aircraft_name(doc: str):
    doc_dict = json.loads(doc)
    return doc_dict["aircraft"]

def get_simulation_name(doc: str):
    doc_dict = json.loads(doc)
    return doc_dict["name"]

@frappe.whitelist()
def start_simulation(doc: str):
    simulation_name = get_simulation_name(doc)
    service = SimulatorService()
    service.start_simulation(simulation_name)
    return True

@frappe.whitelist()
def stop_simulation(doc: str):
    simulation_name = get_simulation_name(doc)
    service = SimulatorService()
    service.stop_simulation(simulation_name)
    return True

@frappe.whitelist()
def reset_aircraft(doc: str):
    aircraft_name = get_aircraft_name(doc)
    service = SimulatorService()
    service.reset_aircraft(aircraft_name)
    return True

@frappe.whitelist()
def launch_aircraft(doc: str):
    aircraft_name = get_aircraft_name(doc)
    service = SimulatorService()
    service.launch_aircraft(aircraft_name)
    return True
