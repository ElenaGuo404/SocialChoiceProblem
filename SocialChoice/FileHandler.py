import ast
import itertools
import random
from collections import OrderedDict


class FileHandler:
    def __init__(self, filename):
        self.filename = filename
        self.metadata = {}
        self.data = []
        self.num_alternatives = 0
        self.votes_dict = {}

        self.extract_information()
        self.create_dict()

    def extract_information2(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

            in_metadata = True
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    key_value = line.lstrip('#').strip().split(': ', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        self.metadata[key] = value

                        if key == 'NUMBER ALTERNATIVES':
                            self.num_alternatives = int(value)
                else:
                    in_metadata = False
                    if ':' in line:
                        voter_id, votes = line.split(': ')
                        voter_id = int(voter_id)

                        # Check if the votes contain sets
                        if '{' in votes:
                            # Extract sets properly by evaluating the string
                            votes = eval(votes)
                        else:
                            votes = list(map(int, votes.split(',')))

                        self.data.append((voter_id, votes))
                    else:
                        in_metadata = True

    def extract_information(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

            in_metadata = True
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    key_value = line.lstrip('#').strip().split(': ', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        self.metadata[key] = value

                        if key == 'NUMBER ALTERNATIVES':
                            self.num_alternatives = int(value)
                else:
                    in_metadata = False
                    if ':' in line:
                        voter_id, votes = line.split(': ')
                        voter_id = int(voter_id)

                        # Check if the votes contain sets
                        if '{' in votes and '}' in votes:
                            # Combine adjacent sets into a single set with ordered keys
                            votes = list(self.combine_adjacent_sets(votes))
                        else:
                            votes = list(map(int, votes.split(',')))

                        self.data.append((voter_id, votes))
                    else:
                        in_metadata = True

    def combine_adjacent_sets(self, votes):
        combined_set = []
        current_set = None

        for char in votes:
            if char == '{':
                current_set = set()
            elif char == '}':
                combined_set.append(tuple(sorted(current_set)))
                current_set = None
            elif char.isdigit():
                if current_set is not None:
                    current_set.add(int(char))
                else:
                    combined_set.append(int(char))

        return OrderedDict.fromkeys(combined_set)

    def get_metadata(self):
        return self.metadata

    def get_data(self):
        return self.data

    def get_num_alternatives(self):
        return self.num_alternatives

    def create_dict(self):

        for voter_num, voter_prefer in self.data:
            self.add_entry(self.votes_dict, voter_prefer, voter_num)

    def add_entry(self, votes_dict, voter_prefer, voter_num):
        key = tuple(voter_prefer)
        if key in votes_dict:
            # If the key already exists, add the values
            votes_dict[key] += voter_num
        else:
            # If the key is not present, create a new entry
            votes_dict[key] = voter_num

            # Check if there are sets in the preferences
            for alt in key:
                if isinstance(alt, set):
                    # If an alternative is a set, create additional entries
                    set_key = frozenset(alt)
                    self.add_entry(votes_dict, set_key, voter_num)

    # file handler to make file become strict - no tie.
    def generate_strict_file(self):
        updated_data = []

        for voter_id, votes in self.data:
            strict_votes = self.get_strict_order(votes)
            updated_data.append((voter_id, strict_votes))

        self.data = updated_data

        # Update the content of the file
        with open(self.filename, 'w') as file:
            # Write metadata
            for key, value in self.metadata.items():
                file.write(f'# {key}: {value}\n')

            # Write updated data
            for voter_id, votes in self.data:
                formatted_votes = [str(alt) if not isinstance(alt, (set, tuple)) else ', '.join(map(str, alt)) for alt
                                   in
                                   votes]
                file.write(f'{voter_id}: {", ".join(formatted_votes)}\n')

    def get_strict_order(self, votes):
        strict_votes = []

        for alt in votes:
            if isinstance(alt, (set, tuple)):
                # If the alternative is a set or tuple, shuffle its elements
                shuffled_alternative = random.sample(alt, len(alt))
                strict_votes.extend(shuffled_alternative)
            else:
                # If the alternative is not a set or tuple, keep it in the strict order
                strict_votes.append(alt)

        return strict_votes

    # file handler to make file become complete.
    def generate_complete_file(self):

        num_alternatives = int(self.get_num_alternatives())
        all_alternatives = set(range(1, num_alternatives + 1))
        updated_data = []

        # Check and update preferences for missing alternatives
        for voter_id, votes in self.data:
            missing_alternatives = all_alternatives - set(votes)

            if missing_alternatives:
                updated_votes = list(votes) + sorted(missing_alternatives)
                updated_votes = self.randomize_missing(updated_votes, missing_alternatives)
                updated_data.append((voter_id, updated_votes))

            else:
                # If no missing alternatives, keep the original data
                updated_data.append((voter_id, votes))

        self.data = updated_data

        # Update the content of the file
        with open(self.filename, 'w') as file:
            for key, value in self.metadata.items():
                file.write(f'# {key}: {value}\n')

            for voter_id, votes in self.data:
                file.write(f'{voter_id}: {",".join(map(str, votes))}\n')

    # Helper functions to get randomized alternatives.
    def randomize_missing(self, updated_votes, missing_alternatives):
        # Create a list of missing alternatives in random order
        missing_list = list(missing_alternatives)
        randomized_missing = random.sample(missing_list, len(missing_list))

        # Replace the missing alternatives in updated_votes with the randomized order
        for i, alt in enumerate(updated_votes):
            if alt in missing_alternatives:
                updated_votes[i] = randomized_missing.pop(0)

        return updated_votes
