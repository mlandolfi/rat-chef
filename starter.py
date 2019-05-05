from AllStocks import ALL_STOCKS
from FileManager import FileManager
from WeightTrainer import WeightTrainer
from EvaluationFunctions import ALL_EVALUATION_FUNCTIONS

def main():
	testStock = ALL_STOCKS["google"]
	fileManager = FileManager("../../Dropbox/")
	fileManager.loadValues(testStock)
	weightTrainer = WeightTrainer(ALL_EVALUATION_FUNCTIONS, testStock, 10000)
	weightTrainer.predictConclusions()
	weightTrainer.storeConclusions()










# runs the main() function
if __name__ == "__main__":
	main()