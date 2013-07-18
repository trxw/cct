from common.abstractdevices.script_scanner.scan_methods import experiment
from drift_tracker_ramsey_oneline import drift_tracker_ramsey_oneline
from labrad.units import WithUnit
from treedict import TreeDict

class drift_tracker_ramsey_trusted_cavity(experiment):
    
    name = 'DriftTrackerRamseyTrustedCavity'
    
    required_parameters = [
        ]

    required_parameters.extend(drift_tracker_ramsey_oneline.required_parameters)
    required_parameters.remove(('DriftTrackerRamsey','line_selection'))
    required_parameters.remove(('DriftTrackerRamsey','pi_time'))
    required_parameters.remove(('DriftTrackerRamsey','amplitude'))
    required_parameters.remove(('DriftTrackerRamsey','detuning'))
        
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.ramsey_dt = self.make_experiment(drift_tracker_ramsey_oneline)
        self.ramsey_dt.initialize(cxn, context, ident)
        
    def run(self, cxn, context):
        dt = self.parameters.DriftTracker
        ramsey_dt = self.parameters.DriftTrackerRamsey
        if dt.line_selection_1 == dt.line_selection_2:
            raise Exception ("The two Drift Tracking lines can not be the same")
        replace = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':dt.line_selection_1,
                                       'DriftTrackerRamsey.pi_time':ramsey_dt.line_1_pi_time,
                                       'DriftTrackerRamsey.amplitude':ramsey_dt.line_1_amplitude,
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz'),
                                       })

        self.ramsey_dt.set_parameters(replace)
        self.ramsey_dt.set_progress_limits(0, 100.0)
        frequency_1,excitation = self.ramsey_dt.run(cxn, context)

        

        self.submit_centers(frequency_1, frequency_2)

    def submit_centers(self, center1, center2):
        dt = self.parameters.DriftTracker
        if center1 is not None and center2 is not None:
            submission = [
                          (dt.line_selection_1, center1),
                          (dt.line_selection_2, center2),
                          ]
            self.drift_tracker.set_measurements(submission)
