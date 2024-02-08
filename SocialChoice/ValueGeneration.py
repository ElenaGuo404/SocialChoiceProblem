import random
from FileHandler import FileHandler


class ValueGeneration:
    def __init__(self, data_dict,num_alternative):
        self.data_dict = data_dict
        self.num_alternative = num_alternative


    def calculate_num_alternatives(self):
        # Determine the number of alternatives in the data
        max_alternatives = 0
        for votes in self.data_dict.keys():
            if isinstance(votes, tuple):
                max_alternatives = max(max_alternatives, max(votes))
            else:
                max_alternatives = max(max_alternatives, votes)

        return max_alternatives
    # value for each alternative is added as sum
    def value_generation2(self):
        generated_values = {}

        for preferences, count in self.data_dict.items():
            max_value = 100
            min_value = 1

            for alternative in preferences:
                # Generate a random value within the range (min_value, max_value)
                value = random.uniform(min_value, max_value)

                # Update the generated values dictionary
                generated_values[alternative] = generated_values.get(alternative, 0) + (value * count)

                # Adjust the range for the next alternative based on the current value
                max_value = value

        return generated_values

    #each row has output
    def update_data_for_missing_alternatives(self, isMissingZero):
        updated_data = {}

        for votes, count in self.data_dict.items():
            if isinstance(votes, tuple):
                updated_votes = self.update_row_for_missing_alternatives(votes, isMissingZero)
                updated_data[updated_votes] = count
            else:
                updated_data[votes] = count

        self.data_dict = updated_data

    def update_row_for_missing_alternatives(self, votes, isMissingZero):
        # Update a row with missing alternatives based on isMissingZero value
        updated_row = list(votes)
        if isMissingZero:
            # Set missing alternatives to 0
            for alt in range(1, self.num_alternatives + 1):
                if alt not in updated_row:
                    updated_row.append(alt)
                    updated_row.append(0)
        else:
            # Generate random values for missing alternatives smaller than existing ones
            existing_values = [updated_row[i + 1] for i in range(0, len(updated_row), 2)]
            for alt in range(1, self.num_alternatives + 1):
                if alt not in updated_row:
                    updated_row.append(alt)
                    updated_row.append(random.randint(1, min(existing_values, default=1)))

        return tuple(updated_row)

    def value_generation(self, isMissingZero=True):
        generated_values = {}

        for votes, count in self.data_dict.items():
            values = self.generate_values_for_votes(votes, isMissingZero)
            generated_values[votes] = (values, count)

        return generated_values

    def generate_values_for_votes(self, votes, isMissingZero):
        values = {}

        # Collect existing candidates to determine the minimum value for missing ones
        existing_candidates = set()
        for index, candidate in enumerate(votes):
            if isinstance(candidate, tuple):
                existing_candidates.update(candidate)
            else:
                existing_candidates.add(candidate)

        min_value_for_missing = 0 if isMissingZero else self.get_min_value(existing_candidates)

        for index, candidate in enumerate(votes):
            if isinstance(candidate, tuple):
                tuple_value = self.get_value_for_candidate(candidate, min_value_for_missing)
                for alt in candidate:
                    values[alt] = tuple_value
            else:
                values[candidate] = self.get_value_for_candidate(candidate, min_value_for_missing)

        # Handle missing alternatives
        missing_alternatives = set(range(1, max(existing_candidates, default=1) + 1)) - existing_candidates
        for missing_alt in missing_alternatives:
            values[missing_alt] = min_value_for_missing

        return values

    def get_min_value(self, existing_candidates):
        # Determine the minimum value for missing candidates
        return min(existing_candidates, default=0)

    def get_value_for_candidate(self, candidate, min_value_for_missing):
        # Generate a random value for the candidate within the range (1, 100)
        return random.randint(1, 100) if min_value_for_missing == 0 else random.randint(1, min_value_for_missing)