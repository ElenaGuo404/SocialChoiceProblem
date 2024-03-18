import numpy as np
import random
from typing import List
from collections import defaultdict


class ValueGeneration:
    """
    Generates values for voting data based on various distributions and normalization methods.
    Values are randomly generated and alternative with lower ranking must have smaller values.
    Values are generated for each voter's choice (allow repetition of ranking ballot).

    Attributes:
    - data_dict (dict): A dictionary containing voting data.
    - strict_data_dict (dict): A dictionary with strict ordering of alternatives and corresponding data.
    - num_alternatives (int): The total number of alternatives participated.
    - missing_alternatives (set): A set containing missing alternatives.
    - value_list (defaultdict): A defaultdict storing generated values for each ranking.

    Methods:
    - value_generation(output_filename, distribution, is_missing_zero, power_param=2): Generates values for voting data.
    - assign_values(votes, count, distribution, power_param): Assigns values to alternatives based alternative ranking.
    - generate_random_values(count, distribution, power_param, upper_limit): Generates random values based on a distribution.
    - make_data_strict(data_dict): Generates a strict ordering for the given voting data.
    - get_strict_order(alt): Gets a strict order for the given alternative.
    - update_data_with_missing(): Updates each ranking ballot with corresponding missing alternatives.
    - randomize_missing(updated_alt, missing_alternatives): Randomly sample the missing alternative's position in the ballot
    - unit_sum_normalization(): Normalizes values based on the sum of values for each data row.
    - unit_range_normalization(): Normalizes values based on the max value for each data row.
    """

    def __init__(self, data_dict, num_alternatives):
        self.data_dict = data_dict
        self.strict_data_dict = data_dict
        self.num_alternatives = num_alternatives
        self.missing_alternatives = set()
        self.value_list = defaultdict(list)

    def generate_k_instances(self, distribution_list, is_missing_zero):
        k_list = defaultdict(list)

        for distribution, (count, power_param) in distribution_list.items():
            print(distribution, count, power_param)
            instances_for_distribution = []

            for _ in range(count):
                print(distribution)
                instances_for_distribution.append(self.value_generation(distribution, is_missing_zero, power_param))

            k_list.update({distribution: instances_for_distribution})

        return k_list

    """
    Generates values for voting data based on user choices.
    
    Parameters:
    - distribution (str): The distribution used to generate values ('uniform', 'exponential', 'normal', 'power', 'gamma', 'geometric').
    - is_missing_zero (str): Whether missing alternatives should be assigned a value of zero. If False, assign it with random value.
    - power_param (float): Power parameter used in some distributions (default is 2). Detail of choice is explain in generate_random_values(). 
    """

    def value_generation(self, distribution, is_missing_zero, power_param=2):
        # Assign values for original alternatives
        values_dict = {}
        value_list = defaultdict(list)
        for index, (votes, count) in enumerate(self.data_dict.items()):
            values_func = lambda v=votes: self.assign_values(v, self.num_alternatives + 1, distribution, power_param)
            values_dict[index] = values_func

        # Get missing alternatives for each row
        missing_alternatives_dict = self.update_data_with_missing()

        for votes, count in self.strict_data_dict.items():

            # Get missing alternatives for the current row
            missing_alternatives = missing_alternatives_dict.get(votes, set())

            for _ in range(count):
                index = list(self.strict_data_dict.keys()).index(votes)
                values = values_dict[index]().copy()

                if missing_alternatives:

                    # get random value dataset
                    values_list = list(values.items())
                    upper_limit = values_list[len(values) - 1][1]
                    random_value = self.generate_random_values(len(missing_alternatives), distribution, power_param,
                                                               upper_limit)
                    random_value = sorted(random_value, reverse=True)

                    for missing_alt in missing_alternatives:
                        if is_missing_zero == 'True':
                            values[missing_alt] = 0

                        # Assgin with random value draw from same distribution,
                        # but the value mnust be smaller than the alternative who originally is in the ranking ballot.
                        else:
                            values[missing_alt] = random_value[0]
                            random_value.remove(random_value[0])

                # Store the generated values for the current ranking
                value_list[votes].append(values)
        return value_list

    """
    Assigns values to alternatives based on alternative ranking.
    For alternative with tie (in same list), assign with same value. 
    Higher the ranking, higher the value assigned to it. 
    
    Parameters:
    - votes: The preferences for a voter.
    - count: The number of alternatives.
    - distribution (str): The distribution used to generate values.
    - power_param (float): Power parameter used in some distributions.
    
    Returns:
    dict: A dictionary mapping alternatives to generated values.
    """

    def assign_values(self, votes, count, distribution, power_param):
        values = {}
        random_values = self.generate_random_values(count, distribution, power_param)
        flat_votes = [alt if isinstance(alt, int) else list(alt) for alt in votes]
        sorted_votes = sorted(enumerate(flat_votes), key=lambda x: x[0])

        for (_, alt), value in zip(sorted_votes, random_values):
            if isinstance(alt, list):
                # assign the same value to all elements in the list
                for element in alt:
                    values[element] = value
            else:
                # If the alternative is not a list, assign the value based on the original ranking
                values[alt] = value

        return values

    """
    Generates random values based on a specified distribution and power_param.
    
    Parameters:
    - count (int): The number of random values need to generate.
    - distribution (str): The type of distribution used to generate values.
    - power_param (float): Power parameter used in some distributions.
    - upper_limit: The upper limit for the generated values.
    
    Returns:
    List[float]: A list of generated random values.
    """

    def generate_random_values(self, count, distribution, power_param, upper_limit=None) -> List[float]:
        random_values = []

        if distribution == 'Uniform':
            random_values = sorted([random.uniform(0, 1) for _ in range(count)], reverse=True)
        elif distribution == 'Exponential':
            random_values = sorted(np.random.exponential(size=count), reverse=True)
        elif distribution == 'Normal':
            random_values = sorted(np.random.normal(size=count), reverse=True)

        # Draws samples in [0, 1] from a power distribution with positive exponent power_param - 1
        elif distribution == 'Power':
            random_values = sorted(np.random.power(power_param, size=count), reverse=True)

        # Draw samples from a Gamma distribution. The power_param is the shape, must be non-negative.
        elif distribution == 'Gamma':
            random_values = sorted(np.random.gamma(power_param, size=count), reverse=True)

        # Draw samples from the geometric distribution. The power_param is probability of success of an individual trial.
        elif distribution == 'Geometric':
            random_values = sorted(np.random.geometric(p=power_param/10, size=count), reverse=True)

        else:
            raise ValueError(f"Invalid distribution choice: {distribution}")

        if upper_limit is not None:
            # Cap the generated values to the specified upper limit
            for value in random_values:
                if value >= upper_limit:
                    random_values.remove(value)
                    value = self.generate_random_values(1, distribution,power_param, upper_limit)
                    random_values.append(value[0])

        return random_values

    """
    Generates a strict ordering for the given voting data.
    
    Parameters:
    - data_dict (dict): A dictionary containing voting data.
    
    Returns:
    dict: A dictionary with strict ordering of alternatives.
    """

    def make_data_strict(self, data_dict):
        updated_data_dict = {}

        for index, (alt, count) in enumerate(data_dict.items()):
            strict_alt = self.get_strict_order(alt)
            key = (tuple(strict_alt), index)
            updated_data_dict[key] = updated_data_dict.get(key, 0) + count

        return updated_data_dict

    """
    Gets a strict order for the given alternative.
    
    Parameters:
    - alt: The alternative for which to get a strict order.
    
    Returns:
    List: A list containing the strict order of the alternative.
    """

    def get_strict_order(self, alt):
        strict_alt = []

        for elem in alt:
            if isinstance(elem, (set, tuple)):
                shuffled_alternative = random.sample(elem, len(elem))
                strict_alt.extend(shuffled_alternative)
            else:
                strict_alt.append(elem)

        return strict_alt

    """
    Updates each ranking ballot with corresponding missing alternatives.
    
    Returns:
    dict: A dictionary containing missing alternatives for each row.
    """

    def update_data_with_missing(self):
        self.strict_data_dict = self.make_data_strict(self.data_dict)

        num_alternatives = self.num_alternatives
        all_alternatives = set(range(1, num_alternatives + 1))
        updated_data_dict = {}
        missing_alternatives_dict = {}

        for ((alt, index), count) in self.strict_data_dict.items():
            missing_alternatives = all_alternatives - set(alt)

            if missing_alternatives:
                updated_alt = list(alt) + sorted(missing_alternatives)
                updated_alt = self.randomize_missing(updated_alt, missing_alternatives)
                key = (tuple(updated_alt), index)
                updated_data_dict[key] = updated_data_dict.get(key, 0) + count

                # Track missing alternatives for the current row
                missing_alternatives_dict[key] = missing_alternatives
            else:
                key = (alt, index)
                updated_data_dict[key] = count

        self.strict_data_dict = updated_data_dict

        return missing_alternatives_dict

    """
    Randomly sample the missing alternative's position in the ballot
    
    Parameters:
    - updated_alt (list): The ranking ballot.
    - missing_alternatives (set): The set of missing alternatives.
    
    Returns:
    list: The updated alternative with randomized missing alternatives.
    """

    def randomize_missing(self, updated_alt, missing_alternatives):
        original_positions = {alt: i for i, alt in enumerate(updated_alt)}

        missing_list = list(missing_alternatives)
        randomized_missing = random.sample(missing_list, len(missing_list))

        # Update based on the original positions
        for alt in missing_alternatives:
            updated_alt[original_positions[alt]] = randomized_missing.pop(0)

        return updated_alt

    """
    Normalizes values based on the sum of values for each row.
    
    Returns:
    defaultdict: A defaultdict storing normalized values for each ranking.
    """

    def unit_sum_normalization(self, k_list):
        normalized_list = []

        for distribution, instances_for_distribution in k_list.items():
            for instance in instances_for_distribution:
                normalized_values = defaultdict(list)
                for votes, values_list in instance.items():
                    total_sums = []

                    for values in values_list:
                        total_sum = sum(value for alt, value in values.items())
                        total_sums.append(total_sum)

                    # Normalize each value in each row of the current ranking
                    for values, total_sum in zip(values_list, total_sums):
                        normalized_values_row = {}
                        for alt, value in values.items():
                            # Handle division by 0
                            normalized_values_row[alt] = value / total_sum if value != 0 else 0
                        normalized_values[votes].append(normalized_values_row)
                normalized_list.append({distribution: normalized_values})

        return normalized_list

    """
    Normalizes values based on the max value (usually is the value of alternative with index 0) for each row.
    
    Returns:
    defaultdict: A defaultdict storing normalized values for each ranking.
    """

    def unit_range_normalization(self, k_list):
        normalized_list = []

        for distribution, instances_for_distribution in k_list.items():
            for instance in instances_for_distribution:
                normalized_values = defaultdict(list)
                for votes, values_list in instance.items():
                    max_values = []

                    # Find the maximum value
                    for values in values_list:
                        max_value = max(values.values())
                        max_values.append(max_value)

                    # Normalize each value in each row of the current ranking
                    for values, max_value in zip(values_list, max_values):
                        normalized_values_row = {}
                        for alt, value in values.items():

                            normalized_values_row[alt] = value / max_value if value != 0 else 0
                        normalized_values[votes].append(normalized_values_row)
                normalized_list.append({distribution: normalized_values})

        return normalized_list
