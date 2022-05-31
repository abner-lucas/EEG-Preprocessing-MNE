class PerformanceIndividual:
    def __init__(self, events, stimulus, stimulus_dict):
        self.events = events
        self.stimulus = stimulus
        self.stimulus_dict = stimulus_dict
        self.stimulus_idxs_events = []
        self.stimulus_name = []
        self.get_stimulus_idxs()
    
    def get_stimulus_idxs(self):
        for i, x in enumerate(self.events):
            for y in self.stimulus:
                if (x == y).all():
                    self.stimulus_idxs_events.append(i)
                    break
        
    def get_response_time(self):
        response_time = []
        for i in range(len(self.stimulus_idxs_events)):
            response_time.append(self.events[self.stimulus_idxs_events[i]+1][0] - self.events[self.stimulus_idxs_events[i]][0])
        return response_time

    def get_responses(self):
        self.stimulus_name = []
        for i in range(len(self.stimulus_idxs_events)):
            for key, value in self.stimulus_dict.items():
                if self.stimulus[i][2] == value:
                    self.stimulus_name.append(key)

        responses_expected = []
        responses_obtained = []
        for i, name in enumerate(self.stimulus_name):
            if name[-1] == 'R':
                responses_expected.append('different')
            else:
                responses_expected.append('same')

            if self.events[self.stimulus_idxs_events[i]+1][2] == 251:
                responses_obtained.append('same')
            else:
                responses_obtained.append('different')
        return responses_expected, responses_obtained

    def get_accuracy(self):
        responses_expected, responses_obtained = self.get_responses()
        n = len(responses_expected)
        accuracy = 0
        for i in range(n):
            if responses_expected[i] == responses_obtained[i]:
                accuracy += 1
        return accuracy/n