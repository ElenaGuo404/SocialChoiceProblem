import hashlib
import random
from fractions import Fraction
from collections import defaultdict
from collections import Counter


class ValueGeneration:
    def __init__(self, data_dict, num_alternatives):
        self.data_dict = data_dict
        self.original_data_dict = data_dict
        self.num_alternatives = num_alternatives
        self.missing_alternatives = set()
        self.value_generated = defaultdict(list)

    def value_generation(self, output_filename):
        # Assign values for original alternatives
        values_dict = {}
        for index, (votes, count) in enumerate(self.data_dict.items()):
            values_func = lambda v=votes: self.assign_values(v, set())
            values_dict[index] = values_func

        # Get missing alternatives for each row
        missing_alternatives_dict = self.update_data_with_missing()

        with open(output_filename, 'w') as file:
            for votes, count in self.data_dict.items():
                # Get missing alternatives for the current row
                missing_alternatives = missing_alternatives_dict.get(votes, set())

                for _ in range(count):
                    index = list(self.data_dict.keys()).index(votes)
                    values = values_dict[index]().copy()

                    for missing_alt in missing_alternatives:
                        values[missing_alt] = Fraction(0)

                    file.write(f'{votes[0]}: {values}\n')

                    # Store the generated values for the current ranking
                    self.value_generated[votes].append(values)

    def assign_values(self, votes, missing_alternatives):
        values = {}

        random_values = sorted([random.uniform(0, 1) for _ in range(self.num_alternatives + 1)], reverse=True)
        flat_votes = [alt if isinstance(alt, int) else list(alt) for alt in votes]
        sorted_votes = sorted(enumerate(flat_votes), key=lambda x: x[0])

        for (_, alt), value in zip(sorted_votes, random_values):
            if isinstance(alt, list):
                # If the alternative is a list (previously a tuple), assign the same value to all elements in the list
                for element in alt:
                    values[element] = Fraction(value)
            else:
                # If the alternative is not a list, assign the value based on the original ranking
                values[alt] = Fraction(value)

        for missing_alt in missing_alternatives:
            values[missing_alt] = Fraction(0)

        return values

    # Generate strict order for giving data
    def make_data_strict(self, data_dict):
        updated_data_dict = {}

        for index, (alt, count) in enumerate(data_dict.items()):
            strict_alt = self.get_strict_order(alt)
            key = (tuple(strict_alt), index)
            updated_data_dict[key] = updated_data_dict.get(key, 0) + count

        return updated_data_dict

    def get_strict_order(self, alt):
        strict_alt = []

        for elem in alt:
            if isinstance(elem, (set, tuple)):
                shuffled_alternative = random.sample(elem, len(elem))
                strict_alt.extend(shuffled_alternative)
            else:
                strict_alt.append(elem)

        return strict_alt

    # Update the missing alternative set for each row. if no missing, no return
    def update_data_with_missing(self):
        self.data_dict = self.make_data_strict(self.data_dict)

        num_alternatives = self.num_alternatives
        all_alternatives = set(range(1, num_alternatives + 1))
        updated_data_dict = {}
        missing_alternatives_dict = {}

        for ((alt, index), count) in self.data_dict.items():
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

        self.data_dict = updated_data_dict

        return missing_alternatives_dict

    # Helper function to shifting giving alternative set
    def randomize_missing(self, updated_alt, missing_alternatives):
        original_positions = {alt: i for i, alt in enumerate(updated_alt)}

        missing_list = list(missing_alternatives)
        randomized_missing = random.sample(missing_list, len(missing_list))

        # Update the updated_alt based on the original positions
        for alt in missing_alternatives:
            updated_alt[original_positions[alt]] = randomized_missing.pop(0)

        return updated_alt

    def unit_sum_normalization(self):
        normalized_values = defaultdict(list)

        for votes, values_list in self.value_generated.items():
            total_sums = []

            # Sum the values for each alternative in each row of the current ranking
            for values in values_list:
                total_sum = sum(value for alt, value in values.items())
                total_sums.append(total_sum)

            # Normalize each value in each row of the current ranking
            for values, total_sum in zip(values_list, total_sums):
                normalized_values_row = {}
                for alt, value in values.items():
                    normalized_values_row[alt] = value / total_sum
                normalized_values[votes].append(normalized_values_row)

        return normalized_values

    def unit_range_normalization(self):
        normalized_values = defaultdict(list)

        for votes, values_list in self.value_generated.items():
            max_values = []

            # Find the maximum value for each row of the current ranking
            for values in values_list:
                max_value = max(values.values())
                max_values.append(max_value)

            # Normalize each value in each row of the current ranking
            for values, max_value in zip(values_list, max_values):
                normalized_values_row = {}
                for alt, value in values.items():
                    normalized_values_row[alt] = value / max_value
                normalized_values[votes].append(normalized_values_row)

        return normalized_values
