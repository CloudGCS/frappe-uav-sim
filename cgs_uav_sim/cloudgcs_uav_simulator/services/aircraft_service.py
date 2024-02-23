import frappe
from .simulator_service import SimulatorService

def on_aircraft_save(doc, method):
    # todo: there is an update on aircraft.certificate - it is an attachment - so please revisit the simulator_service accordingly
    return False
    if not doc.certificate: return False
    sim_srv = SimulatorService()
    result = sim_srv.create_certificate(doc,doc.is_new())
    return result

