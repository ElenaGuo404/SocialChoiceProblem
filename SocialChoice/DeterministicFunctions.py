class DeterministicFunctions:
    def __init__(self, data_dict):
        self.data_dict = data_dict

    def winner(self,scores):
        # Find the candidate with the highest score
        winner_candidate = max(scores, key=scores.get)
        winner_score = scores[winner_candidate]

        return winner_candidate

    def plurality_rule(self):
        candidate_counts = {}

        for votes, count in self.data_dict.items():
            first_choice = votes[0]
            candidate_counts[first_choice] = candidate_counts.get(first_choice, 0) + count

        # winner = max(candidate_counts, key=candidate_counts.get)
        winner_candidate = self.winner(candidate_counts)
        return winner_candidate

    def borda_rule(self):
        borda_count = {}

        for votes, count in self.data_dict.items():
            num_candidates = len(votes)
            for index, candidate in enumerate(votes):
                borda_points = num_candidates - 1 - index
                borda_count[candidate] = borda_count.get(candidate, 0) + (borda_points * count)

        return borda_count

    def harmonic_rule(self):
        harmonic_points = {}

        for votes, count in self.data_dict.items():
            # num_candidates = len(votes)
            for index, candidate in enumerate(votes):
                harmonic_score = 1 / (index + 1)
                harmonic_points[candidate] = harmonic_points.get(candidate, 0) + (harmonic_score * count)

        return harmonic_points

    def k_approval_rule(self, k):
        k_approval_points = {}

        for votes, count in self.data_dict.items():
            for index, candidate in enumerate(votes[:k]):
                k_approval_points[candidate] = k_approval_points.get(candidate, 0) + count

        return k_approval_points

    def veto_rule(self):
        veto_points = {}

        for votes, count in self.data_dict.items():
            for index, candidate in enumerate(votes[:-1]):
                veto_points[candidate] = veto_points.get(candidate, 0) + count

        return veto_points
