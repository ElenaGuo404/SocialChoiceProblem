import copy
import csv
from collections import defaultdict
from statistics import mean

from flask import Flask, render_template, request, jsonify, send_file
from SocialChoice.FileHandler import FileHandler
from SocialChoice.ValueGeneration import ValueGeneration
from SocialChoice.VotingRules import VotingRules
from SocialChoice.Distortion import Distortion

app = Flask(__name__)

# Global variable to store FileHandler instance
obj1 = None
value_generation = None
voting_rules = None
total_scores = {}
distortion_value = None
value_list = None
filename = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/handle_file', methods=['POST'])
def handle_file():
    global obj1, filename
    file = request.files['file_input']
    if file:
        filename = file.filename
        file.save(filename)

        # Create FileHandler instance
        obj1 = FileHandler(filename)

        # Update messages using AJAX response
        return jsonify({'error': False, 'message': 'Upload Success!'})

    return jsonify({'error': True, 'message': 'No file selected.'})


@app.route('/value_generation', methods=['POST'])
def value_generation():
    global obj1, value_list
    if obj1 is None:
        return jsonify({'error': True, 'message': 'File not processed. Please upload a file first.'})

    # Get parameters from the form
    is_missing_zero = request.form['is_missing_zero']
    k = int(request.form['k'])
    normalization_method = request.form['normalization_method']

    # Initialize a list to store distribution details
    distribution_list = {}

    if k > 1:
        total_count = 0
        # Loop through k to get distribution details
        for i in range(6):
            count = int(request.form[f'count_{i}'])
            if count > 0:
                distribution = request.form[f'distribution_{i}']
                power_param = int(request.form[f'power_param_{i}'])
                distribution_list.update({distribution: (count, power_param)})
                total_count += count

        if k != total_count:
            return jsonify({'error': True,
                            'message': f'Please select {k} distributions. You have currently selected {total_count}.'})
    else:
        # Get parameters from the form
        distribution = request.form['distribution']
        power_param = int(request.form['power_param'])
        distribution_list.update({distribution: (1, power_param)})

    # Process the values using ValueGeneration
    value_generation = ValueGeneration(obj1.votes_dict, obj1.get_num_alternatives())
    k_list = value_generation.generate_k_instance(distribution_list, is_missing_zero)

    if normalization_method == 'unit_sum':
        value_list = value_generation.unit_sum_normalization(k_list)
    elif normalization_method == 'unit_range':
        value_list = value_generation.unit_range_normalization(k_list)
    else:
        return jsonify({'error': True, 'message': 'Invalid normalization method.'})
    print(value_list)

    return jsonify({'error': False, 'message': f'Data Generated for {k} instances!', 'data': f'{value_list}'})


@app.route('/voting_rules', methods=['POST'])
def apply_voting_rules():
    global obj1, value_generation, voting_rules, total_scores
    if obj1 is None:
        return jsonify({'error': True, 'message': 'File not processed. Please upload a file!'})

    obj2 = copy.deepcopy(obj1)

    # Automatically make file complete and strict before applying voting rules
    obj2.voting_rule_init()

    # Get parameters from the form
    voting_rule_choices = request.form.getlist('voting_rule_choices')
    scoring_rule_input = request.form.get('scoring_rule_input', '')

    # Initialize voting rules
    voting_rules = VotingRules(obj2.votes_dict, obj2.get_num_alternatives())

    for voting_rule_choice in voting_rule_choices:
        scores = []
        if voting_rule_choice == 'scoring_rule':
            try:
                scoring_vector = eval(scoring_rule_input)  # Safely evaluate the input as a Python expression
                scores.append(voting_rules.scoring_rule(scoring_vector))
            except Exception as e:
                return jsonify({'error': True, 'message': f'Error parsing scoring rule input: {e}'})
        elif voting_rule_choice == 'plurality_rule':
            scores.append(voting_rules.plurality_rule())
        elif voting_rule_choice == 'borda_rule':
            scores.append(voting_rules.borda_rule())
        elif voting_rule_choice == 'harmonic_rule':
            scores.append(voting_rules.harmonic_rule())
        elif voting_rule_choice == 'k_approval_rule':
            k_approval_value = request.form.get('k_approval_value', '')
            if not k_approval_value.isdigit():
                return jsonify(
                    {'error': True, 'message': 'Invalid value for k_approval_rule. Please enter a valid number.'})
            scores.append(voting_rules.k_approval_rule(int(k_approval_value)))
        elif voting_rule_choice == 'veto_rule':
            scores.append(voting_rules.veto_rule())
        else:
            return jsonify({'error': True, 'message': 'Invalid voting rule choice.'})
        total_scores.update({voting_rule_choice: scores})

    # You can do something with the applied voting rule (e.g., display or save it)
    return jsonify({'error': False, 'message': f'Scores: {total_scores}'})


@app.route('/distortion', methods=['POST'])
def apply_distortion():
    global value_generation, voting_rules, total_scores, distortion_value, value_list, filename
    if value_list is None or total_scores is None:
        return jsonify({'error': True, 'message': 'Value generation or voting rules not applied. Please complete '
                                                  'previous steps.'})

    # Get parameters from the form
    distortion_type = request.form['distortion_type']
    average_distortion = {}
    distortion_list = defaultdict(list)
    distribution_list = []

    for single_instance in value_list:
        for distribution, instances_for_distribution in single_instance.items():
            distribution_list.append(distribution)

            print(instances_for_distribution)
            # Initialize distortion
            distortion = Distortion(instances_for_distribution)

            # Apply the chosen distortion type
            for voting_rule, scores in total_scores.items():
                for score in scores:
                    if distortion_type == 'deterministic':
                        winner = voting_rules.winner_determinstic(score)
                        distortion_value = distortion.distortion(winner)

                    elif distortion_type == 'randomize':
                        k_value = int(request.form['k_value'])
                        winner = voting_rules.winner_probability(score)
                        distortion_value = distortion.average_distortion(k_value, winner)
                    else:
                        return jsonify({'error': True, 'message': 'Invalid distortion type.'})

                    distortion_list[voting_rule].append(distortion_value)
    print(distortion_list)

    # Calculate average distortion for each voting rule
    for voting_rule, distortions in distortion_list.items():
        average_distortion.update({voting_rule: mean(distortions)})
    print(average_distortion)

    # Write distortion values to a CSV file
    csv_file_path = 'distortion_values.csv'
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write header row
        writer.writerow(['Distribution'] + distribution_list)
        # Write data rows
        for voting_rule, distortions in distortion_list.items():
            writer.writerow([voting_rule] + distortions)

    return jsonify({'error': False, 'message': f' Average Distortion Value : {average_distortion}'})


if __name__ == '__main__':
    app.run(debug=True)
