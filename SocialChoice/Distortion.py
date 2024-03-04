from collections import defaultdict


class Distortion:
    """
    The Distortion class takes a winner and a dictionary of values as input.
    It calculates the total values for each alternative and provides a distortion measure
    comparing the winner's value with the optimal alternative's value.

    Attributes:
    - winner (str): The chosen winner alternative produced from VotingRules.
    - value_list (dict): A dictionary containing values generated for each alternative from ValueGeneration.
    - total_values (dict): A dictionary containing the total values for each alternative (calculated from value_list).

    Methods:
    - value_calculator(): Calculates the total values for each alternative based on the provided values.
    - distortion(): Calculates the distortion measure comparing the winner's value with the optimal alternative's value.
    """

    def __init__(self, winner, value_list):
        self.winner = winner
        self.value_list = value_list
        self.total_values = self.value_calculator()

    """
    Calculates the total values for each alternative based on the provided values from value_list.
    
    Returns:
    dict: A dictionary containing the total values for each alternative.
    """
    def value_calculator(self):
        total_values = defaultdict(int)

        for ranking_values in self.value_list.values():
            for values in ranking_values:
                for alternative, value in values.items():
                    total_values[alternative] += value

        return dict(total_values)

    """
    Calculates the distortion measure by comparing the winner's total value with the optimal alternative's total value.
    
    Returns:
    float: The distortion value.
    """
    def distortion(self):
        winner_value = self.total_values.get(self.winner, 0)
        optimal_alternative = max(self.total_values, key=self.total_values.get)
        optimal_value = self.total_values[optimal_alternative]

        print('-winner-', self.winner,winner_value, '-optimal-',optimal_alternative,optimal_value)
        return optimal_value/winner_value
