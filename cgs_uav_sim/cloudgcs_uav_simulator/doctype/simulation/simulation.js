// Copyright (c) 2024, CloudGCS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Simulation', {
    // This function is triggered when the form is loaded
    onload: function(frm) {
        // Setting the query for the Table MultiSelect field
        frm.set_query('aircraft', function() {
            // Return an object with the filters
            return {
                filters: {
                    'is_simulator_aircraft': true
                }
            };
        });
    },
});
