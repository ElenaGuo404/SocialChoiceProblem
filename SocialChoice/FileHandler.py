class FileHandler:
    def __init__(self, filename):
        self.filename = filename
        self.metadata = {}
        self.data = []

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
                else:
                    in_metadata = False
                    if ':' in line:
                        voter_id, votes = line.split(': ')
                        voter_id = int(voter_id)
                        votes = list(map(int, votes.split(',')))
                        self.data.append((voter_id, votes))
                    else:
                        in_metadata = True

    def get_metadata(self):
        return self.metadata

    def get_data(self):
        return self.data

    def create_dict(self):
        votes_dict = {}
        for voter_num, voter_prefer in self.data:
            votes_dict[tuple(voter_prefer)] = voter_num
        return votes_dict



