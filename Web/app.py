# from flask import Flask, render_template, request
# from SocialChoice.FileHandler import FileHandler
# from SocialChoice.ValueGeneration import ValueGeneration
# from SocialChoice.VotingRules import VotingRules
# from SocialChoice.Distortion import Distortion
#
# app = Flask(__name__)
#
# # Global variable to store FileHandler instance
# filehandler = None
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/handle_file', methods=['POST'])
# def handle_file():
#     global filehandler
#     file = request.files['file_input']
#     if file:
#         filename = file.filename
#         file.save(filename)
#
#         # Create FileHandler instance
#         filehandler = FileHandler(filename)
#         num_alternatives = filehandler.get_num_alternatives()
#
#         # Update the HTML template with the relevant information
#         message = f'The number of alternatives in the file is: {num_alternatives}'
#         return render_template('index.html', message=message)
#     else:
#         return 'No file selected.'
#
#
# @app.route('/value_generation', methods=['POST'])
# def value_generation():
#     global filehandler
#     if filehandler is None:
#         return 'File not processed. Please upload a file first.'
#
#     # Get parameters from the form
#     is_missing_zero = request.form['is_missing_zero']
#     distribution = request.form['distribution']
#     output_filename = request.form['output_filename']
#     power_param = int(request.form['power_param'])
#
#     # Process the values using ValueGeneration
#     value_generation = ValueGeneration(filehandler.votes_dict, filehandler.get_num_alternatives())
#     value_generation.value_generation(output_filename, distribution, is_missing_zero, power_param)
#     value_list = value_generation.unit_sum_normalization()
#
#     # You can do something with the generated values (e.g., display or save them)
#     return f'Generated values: {value_list}'
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
from SocialChoice.FileHandler import FileHandler
from SocialChoice.ValueGeneration import ValueGeneration
from SocialChoice.VotingRules import VotingRules
from SocialChoice.Distortion import Distortion

app = Flask(__name__)

# Global variable to store FileHandler instance
obj1 = None
value_generation = None
voting_rules = None
scores = {}
distortion_value = None
value_list = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/handle_file', methods=['POST'])
def handle_file():
    global obj1
    file = request.files['file_input']
    if file:
        filename = file.filename
        file.save(filename)

        # Create FileHandler instance
        obj1 = FileHandler(filename)
        num_alternatives = obj1.get_num_alternatives()

        # Update messages using AJAX response
        return jsonify({'message': f'The number of alternatives in the file is: {num_alternatives}'})

    return jsonify({'message': 'No file selected.'})


@app.route('/value_generation', methods=['POST'])
def value_generation():
    global obj1, value_generation, value_list
    if obj1 is None:
        return jsonify({'message': 'File not processed. Please upload a file first.'})

    # Get parameters from the form
    is_missing_zero = request.form['is_missing_zero']
    distribution = request.form['distribution']
    output_filename = request.form['output_filename']
    power_param = int(request.form['power_param'])

    # Get the chosen normalization method
    normalization_method = request.form['normalization_method']

    # Process the values using ValueGeneration
    value_generation = ValueGeneration(obj1.votes_dict, obj1.get_num_alternatives())
    value_generation.value_generation(output_filename, distribution, is_missing_zero, power_param)

    # Apply the chosen normalization method
    if normalization_method == 'unit_sum':
        value_list = value_generation.unit_sum_normalization()
    elif normalization_method == 'unit_range':
        value_list = value_generation.unit_range_normalization()
    else:
        return jsonify({'message': 'Invalid normalization method.'})

    # You can do something with the generated values (e.g., display or save them)
    return jsonify({'message': f'Data Generated!', 'data': f'{value_list}'})


@app.route('/voting_rules', methods=['POST'])
def apply_voting_rules():
    global obj1, value_generation, voting_rules, scores
    if obj1 is None:
        return jsonify({'message': 'File not processed. Please upload a file!'})

    # Get parameters from the form
    voting_rule_choice = request.form['voting_rule_choices']
    scoring_rule_input = request.form.get('scoring_rule_input', '')

    # Initialize voting rules
    voting_rules = VotingRules(obj1.votes_dict, obj1.get_num_alternatives())

    # Apply the chosen voting rule
    if voting_rule_choice == 'scoring_rule':
        try:
            scoring_vector = eval(scoring_rule_input)  # Safely evaluate the input as a Python expression
            scores = voting_rules.scoring_rule(scoring_vector)
        except Exception as e:
            return jsonify({'message': f'Error parsing scoring rule input: {e}'})
    elif voting_rule_choice == 'plurality_rule':
        scores = voting_rules.plurality_rule()
    elif voting_rule_choice == 'borda_rule':
        scores = voting_rules.borda_rule()
    elif voting_rule_choice == 'harmonic_rule':
        scores = voting_rules.harmonic_rule()
    elif voting_rule_choice == 'k_approval_rule':
        k_approval_value = request.form.get('k_approval_value', '')
        if not k_approval_value.isdigit():
            return jsonify({'message': 'Invalid value for k_approval_rule. Please enter a valid number.'})
        scores = voting_rules.k_approval_rule(int(k_approval_value))
    elif voting_rule_choice == 'veto_rule':
        scores = voting_rules.veto_rule()
    else:
        return jsonify({'message': 'Invalid voting rule choice.'})

    # You can do something with the applied voting rule (e.g., display or save it)
    return jsonify({'message': f'Scores: {scores}'})


@app.route('/make_file_complete_strict', methods=['POST'])
def make_file_complete_strict():
    global obj1, value_generation, voting_rules
    if obj1 is None:
        return jsonify({'message': 'File not processed. Please upload a file!'})

    # Initialize voting rule
    obj1.voting_rule_init()

    return jsonify({'message': 'File made complete and strict.'})


@app.route('/distortion', methods=['POST'])
def apply_distortion():
    global value_generation, voting_rules, scores, distortion_value, value_list
    if value_generation is None or voting_rules is None or scores is None:
        return jsonify({'message': 'Value generation or voting rules not applied. Please complete previous steps.'})

    # Get parameters from the form
    distortion_type = request.form['distortion_type']

    # Initialize distortion
    distortion = Distortion(value_list)

    # Apply the chosen distortion type
    if distortion_type == 'deterministic':
        winner = voting_rules.winner_single(scores)
        distortion_value = distortion.distortion(winner)
    elif distortion_type == 'randomize':
        k_value = int(request.form['k_value'])
        winner = voting_rules.winner_probability(scores)
        distortion_value = distortion.average_distortion(k_value, winner)
    else:
        return jsonify({'message': 'Invalid distortion type.'})

    return jsonify({'message': f'Winner is {winner}, Distortion Value: {distortion_value}'})


if __name__ == '__main__':
    app.run(debug=True)
