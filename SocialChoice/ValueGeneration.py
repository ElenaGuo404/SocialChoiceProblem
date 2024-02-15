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

    # def value_generation(self, output_filename):
    #     # Get missing alternatives for each row
    #     missing_alternatives_dict = self.update_data_with_missing()
    #
    #     with open(output_filename, 'w') as file:
    #         for votes, count in self.data_dict.items():
    #             # Get missing alternatives for the current row
    #             missing_alternatives = missing_alternatives_dict.get(votes, set())
    #
    #             for _ in range(count):
    #                 values = self.assign_values(votes[0], missing_alternatives)
    #                 # file.write(f'{votes}: {values}\n')
    #                 file.write(f'{votes[0]}: {values}\n')

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
                    # Use the index to get the function and call it to retrieve values
                    index = list(self.data_dict.keys()).index(votes)
                    values = values_dict[index]().copy()
                    # Assign values to missing alternatives
                    for missing_alt in missing_alternatives:
                        values[missing_alt] = Fraction(0)

                    file.write(f'{votes[0]}: {values}\n')

    def assign_values(self, votes, missing_alternatives):
        values = {}

        # Generate random values and sort them
        random_values = sorted([random.uniform(0, 1) for _ in range(self.num_alternatives + 1)], reverse=True)

        # Flatten the votes structure to a list of alternatives
        flat_votes = [alt if isinstance(alt, int) else list(alt) for alt in votes]

        # Sort the alternatives based on the original ranking
        sorted_votes = sorted(enumerate(flat_votes), key=lambda x: x[0])

        # Assign values based on the original ranking
        for (_, alt), value in zip(sorted_votes, random_values):
            if isinstance(alt, list):
                # If the alternative is a list (previously a tuple), assign the same value to all elements in the list
                for element in alt:
                    values[element] = Fraction(value)
            else:
                # If the alternative is not a list, assign the value based on the original ranking
                values[alt] = Fraction(value)

        # Assign values to missing alternatives
        for missing_alt in missing_alternatives:
            values[missing_alt] = Fraction(0)

        return values



    def make_data_strict(self, data_dict):
        updated_data_dict = {}

        for alt, count in data_dict.items():
            strict_alt = self.get_strict_order(alt)
            updated_data_dict[tuple(strict_alt)] = updated_data_dict.get(tuple(strict_alt), 0) + count

        return updated_data_dict

    # def make_data_strict(self):
    #     updated_data_dict = {}
    #
    #     for index, (alt, count) in enumerate(self.data_dict.items()):
    #         strict_alt = self.get_strict_order(alt)
    #         updated_data_dict[(tuple(strict_alt), index)] = count
    #
    #     self.data_dict = updated_data_dict
    #
    # def get_strict_order(self, alt):
    #     strict_alt = []
    #
    #     for elem in alt:
    #         if isinstance(elem, (set, tuple)):
    #             shuffled_alternative = random.sample(elem, len(elem))
    #             strict_alt.extend(shuffled_alternative)
    #         else:
    #             strict_alt.append(elem)
    #
    #     return strict_alt


    def get_strict_order(self, alt):
        strict_alt = []

        for elem in alt:
            if isinstance(elem, (set, tuple)):
                shuffled_alternative = random.sample(elem, len(elem))
                strict_alt.extend(shuffled_alternative)
            else:
                strict_alt.append(elem)

        return strict_alt

    def update_data_with_missing(self):
        self.data_dict = self.make_data_strict(self.data_dict)

        num_alternatives = self.num_alternatives
        all_alternatives = set(range(1, num_alternatives + 1))
        updated_data_dict = {}
        missing_alternatives_dict = {}  # Track missing alternatives for each row

        for index, (alt, count) in enumerate(self.data_dict.items()):
            missing_alternatives = all_alternatives - set(alt)

            if missing_alternatives:
                updated_alt = list(alt) + sorted(missing_alternatives)
                updated_alt = self.randomize_missing(updated_alt, missing_alternatives)
                key = (tuple(updated_alt), index)  # Use a tuple (ranking, index) as the key
                updated_data_dict[key] = updated_data_dict.get(key, 0) + count

                # Track missing alternatives for the current row
                missing_alternatives_dict[key] = missing_alternatives
            else:
                # If no missing alternatives, keep the original data
                key = (alt, index)  # Use a tuple (ranking, index) as the key
                updated_data_dict[key] = count

        self.data_dict = updated_data_dict

        return missing_alternatives_dict

    # def update_data_with_missing(self):
    #     self.make_data_strict()
    #     print(self.data_dict)
    #
    #     num_alternatives = self.num_alternatives
    #     all_alternatives = set(range(1, num_alternatives + 1))
    #     updated_data_dict = {}
    #     missing_alternatives_dict = {}  # Track missing alternatives for each row
    #
    #     for index, (alt, count) in enumerate(self.data_dict.items()):
    #         missing_alternatives = all_alternatives - set(alt)
    #
    #         if missing_alternatives:
    #             updated_alt = list(alt) + sorted(missing_alternatives)
    #             updated_alt = self.randomize_missing(updated_alt, missing_alternatives)
    #             key = (tuple(updated_alt), index)  # Use a tuple (ranking, index) as the key
    #             updated_data_dict[key] = updated_data_dict.get(key, 0) + count
    #
    #             # Track missing alternatives for the current row
    #             missing_alternatives_dict[key] = missing_alternatives
    #         else:
    #             # If no missing alternatives, keep the original data
    #             key = (alt, index)  # Use a tuple (ranking, index) as the key
    #             updated_data_dict[key] = count
    #
    #     self.data_dict = updated_data_dict
    #
    #     return missing_alternatives_dict


    def randomize_missing(self, updated_alt, missing_alternatives):
        # Store the original position of the alternatives
        original_positions = {alt: i for i, alt in enumerate(updated_alt)}

        missing_list = list(missing_alternatives)
        randomized_missing = random.sample(missing_list, len(missing_list))

        # Update the updated_alt based on the original positions
        for alt in missing_alternatives:
            updated_alt[original_positions[alt]] = randomized_missing.pop(0)

        return updated_alt




    # def value_generation(self, output_filename):
    #     with open(output_filename, 'w') as file:
    #         for votes, count in self.data_dict.items():
    #             for _ in range(count):
    #                 values = self.assign_values(votes)
    #                 file.write(f'{votes}: {values}\n')
    #
    # def assign_values(self, votes):
    #     values = {}
    #
    #     # Generate random values and sort them
    #     random_values = sorted([random.uniform(0, 1) for _ in range(self.num_alternatives +1 )], reverse=True)
    #
    #     # Flatten the votes structure to a list of alternatives
    #     flat_votes = [alt if isinstance(alt, int) else list(alt) for alt in votes]
    #
    #     # Sort the alternatives based on the original ranking
    #     sorted_votes = sorted(enumerate(flat_votes), key=lambda x: x[0])
    #
    #     # Assign values based on the original ranking
    #     for (_, alt), value in zip(sorted_votes, random_values):
    #         if isinstance(alt, list):
    #             # If the alternative is a list (previously a tuple), assign the same value to all elements in the list
    #             for element in alt:
    #                 values[element] = Fraction(value)
    #         else:
    #             # If the alternative is not a list, assign the value based on the original ranking
    #             values[alt] = Fraction(value)
    #
    #     return values
