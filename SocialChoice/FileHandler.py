import random
from collections import OrderedDict


class FileHandler:
    """
    Handles the processing and manipulation of a single data file.

    Attributes:
    - filename (str): The name of the input file.
    - metadata (dict): A dictionary containing metadata(all information) extracted from the file.
    - original_data (list): A list containing the original rank ballot with corresponding number of voters who support this ballot as tuples.
    - data (list): A list containing the same data as original_data, but used for later data manipulation.
    - num_alternatives (int): The total number of alternatives participated.
    - votes_dict (dict): A dictionary representation of the voting data.

    Methods:
    - voting_rule_init(): Calling required methods to ensure the data is ready for VotingRules.
    - extract_information(): Extracts metadata and original data from the input file.
    - combine_adjacent_sets(votes): Combines adjacent sets in the votes string.
    - get_metadata(): Returns the metadata extracted from the file.
    - get_data(): Returns the voter data after extraction and processing.
    - get_num_alternatives(): Returns the total number of alternatives.
    - create_dict(): Creates a dictionary representation of the voting data.Key is ranking ballot and value is count.
    - add_entry(votes_dict, voter_prefer, voter_num): Adds an entry to the voting data dictionary.
    - generate_strict_file(): Converts the file to a strict order file (no ties between alternatives).
    - get_strict_order(votes): Gets the strict order for alternatives from the votes.
    - generate_complete_file(): Converts the file to a complete order file.
    - randomize_missing(updated_votes, missing_alternatives): Randomly sample the missing alternative's position in the ballot
    """
    def __init__(self, filename):
        self.filename = filename
        self.metadata = {}
        self.original_data = []
        self.data = []
        self.num_alternatives = 0
        self.votes_dict = {}

        self.extract_information()
        self.create_dict()

    """
    Calling required methods to ensure the data is ready for VotingRules.
    """
    def voting_rule_init(self):
        self.generate_strict_file()
        self.generate_complete_file()
        self.create_dict()

    """
    Extracts metadata and original data from the input file.    
    """
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
                            votes = list(self.combine_adjacent_sets(votes))
                        else:
                            votes = list(map(int, votes.split(',')))

                        self.original_data.append((voter_id, votes))
                    else:
                        in_metadata = True
        self.data = self.original_data

    """
    Combines adjacent sets in the votes string.
    
    Parameters:
    - votes (str): The votes string.
    
    Returns:
    OrderedDict: A dictionary representation of combined sets.
    """
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

    """
    Returns the metadata extracted from the file.
    
    Returns:
    dict: A dictionary containing metadata.
    """
    def get_metadata(self):
        return self.metadata

    """
    Returns the voter data after extraction and processing.
    
    Returns:
    list: A list containing voter data as tuples.
    """
    def get_data(self):
        return self.data

    """
    Returns the total number of alternatives.
    
    Returns:
    int: The total number of alternatives.
    """
    def get_num_alternatives(self):
        return self.num_alternatives

    """
    Creates a dictionary representation of the voting data.Key is ranking ballot and value is count.
    """
    def create_dict(self):
        self.votes_dict = {}

        for voter_num, voter_prefer in self.data:
            self.add_entry(self.votes_dict, voter_prefer, voter_num)

    """
    Adds an entry to the voting data dictionary.

    Parameters:
    - votes_dict (dict): The voting data dictionary.
    - voter_prefer: The voter's preferences (ranking ballot).
    - voter_num (int): The number of voters.
    """
    def add_entry(self, votes_dict, voter_prefer, voter_num):
        key = tuple(voter_prefer)

        if key in votes_dict:
            votes_dict[key] += voter_num
        else:
            votes_dict[key] = voter_num

            # Check if there are sets in the preferences
            for alt in key:
                if isinstance(alt, set):
                    set_key = frozenset(alt)
                    self.add_entry(votes_dict, set_key, voter_num)

    """
    Converts the file to a strict order file (no ties between alternatives).
    """
    def generate_strict_file(self):
        updated_data = []

        for voter_id, votes in self.data:
            strict_votes = self.get_strict_order(votes)
            updated_data.append((voter_id, strict_votes))

        self.data = updated_data

    """
   Gets the strict order for alternatives from the votes.

    Parameters:
    - votes (list): The ranking ballot.

    Returns:
    list: The strict order of ranking (no alternatives are inside a set).
    """
    def get_strict_order(self, votes):
        strict_votes = []

        for alt in votes:
            if isinstance(alt, (set, tuple)):
                shuffled_alternative = random.sample(alt, len(alt))
                strict_votes.extend(shuffled_alternative)

            else:
                strict_votes.append(alt)

        return strict_votes

    """
    Converts the file to a complete order file.
    """
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
                updated_data.append((voter_id, votes))

        self.data = updated_data

    """
    Randomly sample the missing alternative's position in the ballot
    
    Parameters:
    - updated_votes (list): The ranking ballot.
    - missing_alternatives (set): The set of missing alternatives.
    
    Returns:
    list: The updated ranking ballot.
    """
    def randomize_missing(self, updated_votes, missing_alternatives):

        missing_list = list(missing_alternatives)
        randomized_missing = random.sample(missing_list, len(missing_list))

        for i, alt in enumerate(updated_votes):
            if alt in missing_alternatives:
                updated_votes[i] = randomized_missing.pop(0)

        return updated_votes
