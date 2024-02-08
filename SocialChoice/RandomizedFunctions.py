import random

class RandomizedFunctions:

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def winner_probability(self):
        total_scores = sum(self.data_dict.values())

        # Calculate the probability for each alternative
        probabilities = {candidate: score / total_scores for candidate, score in self.data_dict.items()}

        return probabilities

    def winner_randomized(self):
        probabilities = self.winner_probability()

        # Randomly select a winner based on probabilities
        winner_candidate = random.choices(list(probabilities.keys()), weights=list(probabilities.values()))[0]

        return winner_candidate

