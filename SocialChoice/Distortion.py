from collections import defaultdict
import random


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

    def __init__(self, value_list):
        self.value_list = value_list
        self.total_values = self.value_calculator(self.value_list)

    """
    Calculates the total values for each alternative based on the provided values from value_list.
    
    Parameters:
    
    
    Returns:
    dict: A dictionary containing the total values for each alternative.
    """

    def value_calculator(self, value_list):
        total_values = defaultdict(int)

        for ranking_values in value_list.values():
            for values in ranking_values:
                for alternative, value in values.items():
                    total_values[alternative] += value

        return dict(total_values)

    """
    Calculates the distortion measure by comparing the winner's total value with the optimal alternative's total value.
    
    Parameters:
    - winner(int/dict): The winner alternative / the winner alternative probability list
    
    Returns:
    float: The distortion value.
    """

    def distortion(self, winner):
        optimal_alternative = max(self.total_values, key=self.total_values.get)
        optimal_value = self.total_values[optimal_alternative]
        winner_value = 0

        # For deterministic, it will output a single winner
        if isinstance(winner, int):
            winner_value = self.total_values.get(winner, 0)

        # For Randomized voting rules, it will output a list of probability
        elif isinstance(winner, dict):
            for alternative, probability in winner.items():
                alternative_value = self.total_values.get(alternative, 0)
                winner_value += probability * alternative_value

        print('-winner-', winner, winner_value, '-optimal-', optimal_alternative, optimal_value)
        return optimal_value / winner_value


    """
    For given probability list, generate winner for multiple trials and for each winner, run the distortion and get average distortion across them.
    
    Parameters:
    - k(int): User input, indicating number of trails 
    - probability_list(dict): a dictionary containing alternative as key and their probability of getting selected as values.
    
    Returns:
    float: The average distortion across trials.  
    
    """
    def average_distortion(self, k, probability_list):
        distortion_results = defaultdict(list)

        for _ in range(k):
            winner = random.choices(list(probability_list.keys()), weights=list(probability_list.values()))[0]
            distortion_value = self.distortion(winner)
            distortion_results[winner].append(distortion_value)

        all_distortions = [distortion for distortions in distortion_results.values() for distortion in distortions]
        overall_average_distortion = sum(all_distortions) / len(all_distortions)
        print(all_distortions)

        return overall_average_distortion
