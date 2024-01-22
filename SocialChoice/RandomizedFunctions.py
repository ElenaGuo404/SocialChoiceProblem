class RandomizedFunctions:

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def winner_probability(self, x):
        total_scores = sum(self.data_dict.values())

        probability_x = self.data_dict.get(x, 0) / total_scores
        return probability_x

    def x(self):

        return

