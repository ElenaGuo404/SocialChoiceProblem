class DeterministicFunctions:
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.num_candidates = max(len(votes) for votes in self.data_dict.keys())

    def winner(self, scores):

        # Find the candidate with the highest score
        winner_candidate = max(scores, key=scores.get)
        winner_score = scores[winner_candidate]

        return winner_candidate

    def scoring_rule(self, weights):
        scores = {}

        for votes, count in self.data_dict.items():
            for index, candidate in enumerate(votes):
                scores[candidate] = scores.get(candidate, 0) + (weights[index] * count)

        return scores

    def plurality_rule(self):

        # Use the k_approval_rule with k=1 for plurality
        plurality_points = self.k_approval_rule(1)
        return plurality_points

    def borda_rule(self):

        # Create a default Borda weights vector
        weights_vector = [self.num_candidates - 1 - i for i in range(self.num_candidates)]
        borda_points = self.scoring_rule(weights_vector)

        return borda_points

    def harmonic_rule(self):

        # Create the default harmonic scoring vector
        harmonic_vector = [1 / (i + 1) for i in range(self.num_candidates)]
        harmonic_points = self.scoring_rule(harmonic_vector)

        return harmonic_points

    def k_approval_rule(self, k):

        # Create a modified weights vector for k-approval
        weights_vector = [1 if i < k else 0 for i in range(self.num_candidates)]
        k_approval_points = self.scoring_rule(weights_vector)

        return k_approval_points

    def veto_rule(self):
        # Use the k_approval_rule with k=m-1 for veto, m is the number of alternatives
        veto_points = self.k_approval_rule(self.num_candidates - 1)

        return veto_points

