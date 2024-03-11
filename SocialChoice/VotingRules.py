import random


class VotingRules:
    """
    Implements various voting rules for determining winners in a multi-candidate election.

    Attributes:
    - data_dict (dict): A dictionary containing ranking and corresponding counts(number of votes).
    - num_candidates (int): The total number of candidates in the election.

    Methods:
    - winner_single(scores): Output a single winner candidate by highest scores.
    - winner_randomized(scores): Output a single winner by randomized selection with weight(different probabilities for each alternative).
    - winner_probability(scores): Calculates the probability for each candidate based on their scores.
    - scoring_rule(weights): Computes the scores for each candidate by a user input weight vector.
    - plurality_rule(): Applies the scoring_rule to determine the winner with weight vector [1,0,0,...0].
    - borda_rule(): Applies the scoring_rule to determine the winner with weight vector [m-1,m-2,m-3,...0].
    - harmonic_rule(): Applies the scoring_rule to determine the winner with weight vector [1,1/2,1/3,...1/m].
    - k_approval_rule(k): Applies the scoring_rule to determine the winner with weight vector [1,1,1,...0]. assign '1' to k number of candidates.
    - veto_rule():Applies the scoring_rule to determine the winner with weight vector [1,1,1,...1,0].
    """

    def __init__(self, data_dict, num_candidates):
        self.data_dict = data_dict
        self.num_candidates = num_candidates

    """
    Determines a single winner candidate by highest scores.
    
    Parameters:
    - scores (dict): A dictionary containing the total scores of each candidate.
    
    Returns:
    str: The candidate who is the winner.
    """

    def winner_determinstic(self, scores):

        winner_candidate = max(scores, key=scores.get)
        winner_score = scores[winner_candidate]

        return winner_candidate

    """
    Determines a single winner by randomized selection with weight vector.

    Parameters:
    - scores (dict): A dictionary containing the total scores of each candidate.

    Returns:
    str: The randomly selected winner.
    """

    def winner_randomized(self, scores):
        probabilities = self.winner_probability(scores)

        # Randomly select a winner by applied probabilities weight vector.
        winner_candidate = random.choices(list(probabilities.keys()), weights=list(probabilities.values()))[0]

        return winner_candidate

    """
    Calculates the probability for each candidate based on their scores.

    Parameters:
    - scores (dict): A dictionary containing the total scores of each candidate.

    Returns:
    dict: A dictionary containing the probabilities of each candidate's winning chance.
    """

    def winner_probability(self, scores):
        total_scores = sum(scores.values())

        # Calculate the probability for each alternative
        probabilities = {candidate: score / total_scores for candidate, score in scores.items()}

        return probabilities

    """
    Computes the scores for each candidate by a user input weight vector.
    
    Parameters:
    - weights (list): A weight vector, index corresponding to scores assigned to each candidate in same rank(index).
    
    Returns:
    dict: A dictionary containing the total scores of each candidate.
    """

    def scoring_rule(self, weights):
        scores = {}

        for votes, count in self.get_data().items():
            for index, candidate in enumerate(votes):
                scores[candidate] = scores.get(candidate, 0) + (weights[index] * count)

        return scores

    """
    Applies the scoring_rule to determine the winner with weight vector [1,0,0,...0].
    
    Returns:
    dict: A dictionary containing the total scores of each candidate.
    """

    def plurality_rule(self):

        # Use the k_approval_rule with k=1 for plurality
        plurality_points = self.k_approval_rule(1)
        return plurality_points

    """
    Applies the scoring_rule to determine the winner with weight vector [m-1,m-2,m-3,...0].

    Returns:
    dict: A dictionary containing the total scores of each candidate.
    """

    def borda_rule(self):

        weights_vector = [self.get_num_alternatives() - 1 - i for i in range(self.get_num_alternatives())]
        borda_points = self.scoring_rule(weights_vector)

        return borda_points

    """
    Applies the scoring_rule to determine the winner with weight vector [1,1/2,1/3,...1/m].

    Returns:
    dict: A dictionary containing the total scores of each candidate.
    """

    def harmonic_rule(self):

        harmonic_vector = [1 / (i + 1) for i in range(self.get_num_alternatives())]
        harmonic_points = self.scoring_rule(harmonic_vector)

        return harmonic_points

    """
    Applies the scoring_rule to determine the winner with weight vector [1,1,1,...0] : assign '1' to k number of candidates.

    Returns:
    dict: A dictionary containing the total scores of each candidate.
    """

    def k_approval_rule(self, k):

        weights_vector = [1 if i < k else 0 for i in range(self.get_num_alternatives())]
        k_approval_points = self.scoring_rule(weights_vector)

        return k_approval_points

    """
    Applies the scoring_rule to determine the winner with weight vector [1,1,1,...1,0].

    Returns:
    dict: A dictionary containing the total scores of each candidate.
    """

    def veto_rule(self):

        # Use the k_approval_rule with k=m-1 for veto, m is the number of alternatives
        veto_points = self.k_approval_rule(self.get_num_alternatives() - 1)

        return veto_points

    """
    Returns the total number of alternatives.

    Returns:
    int: The total number of alternatives.
    """

    def get_num_alternatives(self):
        return self.num_candidates

    """
    Returns the dictionary consist of preference voting data.

    Returns:
    dict: The dictionary of voting data.
    """

    def get_data(self):
        return self.data_dict