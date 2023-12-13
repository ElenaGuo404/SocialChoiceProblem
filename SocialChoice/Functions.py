class Functions:
    def __init__(self, data_dict):
        self.data_dict = data_dict

    def majority_rule(self):
        candidate_counts = {}

        for votes, count in self.data_dict.items():
            first_choice = votes[0]
            candidate_counts[first_choice] = candidate_counts.get(first_choice, 0) + count

        winner = max(candidate_counts, key=candidate_counts.get)
        return winner
