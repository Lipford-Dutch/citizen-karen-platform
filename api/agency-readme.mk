Below is a summary of the FastAPI code that adds one POST endpoint for each of the complaint portals you listed.  The implementation relies on a dynamic mapping so that adding new agencies requires only adding new keys to the AGENCY_ENDPOINTS dictionary.  Each endpoint injects a constant agency value into the complaint payload and forwards it to the ComplaintsService, which then dispatches to the appropriate plugin.

Key Code (already in backend/app/api/v1/agency_endpoints.py)
code: agency_endpoints.py
How to use
	•	Each POST request goes to /api/v1/complaints/<path-suffix> with a JSON body containing phone_number, description and timestamp.
	•	For example, to file a CFPB consumer complaint, the client sends a POST to /api/v1/complaints/cfpb-consumer with the required fields.
	•	The suffixes map to the underlying agency plugin keys, so that the system can route complaints correctly.

Evidence for complaint portals
	•	The Department of Justice’s civil-rights portal invites people to “report a civil rights violation” and asks them to describe what happened ￼ ￼.
	•	The Consumer Financial Protection Bureau site explicitly states that users can “Submit a complaint about a financial product or service” and that the CFPB forwards complaints to companies or other regulators for response ￼.

These citations confirm that the listed endpoints correspond to official agency portals for filing complaints.