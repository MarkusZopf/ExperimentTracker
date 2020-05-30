from experiment_tracker import Experiment

# 1. Specify the database connection details.
database_config = {'host': 'localhost', 
                   'port': 3306, 
                   'user': 'root', 
                   'passwd': 'root', 
                   'db': 'experiment_tracker'}

# 2. Create an experiment. The project name is used to determine the table name of the corresponding SQL table. All experiments of the same project will be stored in the same table.
experiment = Experiment(database_config=database_config, project_name='hello_world_project')

# 3. Configure parameters of the project such as dataset name, or learning rate. Each parameter will be stored in an SQL column in the project's SQL table. The columns is created automatically and type of the column is determined based on the type of the value of the parameter. 
experiment.parameters['dataset_train'] = 'train_set'
experiment.parameters['dataset_test'] = 'test_set'
experiment.parameters['learning_rate'] = 0.001
experiment.parameters['num_runs'] = 3
experiment.parameters['use_dropout'] = False

# 4. Run experiments and collect results.
# dataset_train = load_dataset(experiment.parameters['dataset_train'])
# dataset_test = load_dataset(experiment.parameters['dataset_test'])
for seed in range(0, experiment.parameters['num_runs']):
	experiment.parameters['seed'] = seed # add/modify parameters in case they change during an experiment run
	# model = train_model(dataset_train, experiment) # 'experiment' contains all parameters for training, no need to change functions calls after adding additional parameters
	experiment.results['runtime'] = 1.5
	experiment.results['train_loss'] = 0.1

	# evaluation = evaluate_model(dataset_test) # results can be collected at different locations in the code
	experiment.results['test_loss'] = 0.3

	# 5. Save parameters and corresponding results to the database.
	experiment.save_results()

# The stored results can be analyzed later, e.g. by directly querying the database. 
# For example, 'SELECT timestamp, AVG(test_loss) FROM hello_world_project GROUP BY timestamp' computes the average test loss of the three different seeds for each performed experiment run.