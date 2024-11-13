HEURISTICS ?= JeroslowWangOneSidedSolver
FILENAME ?= input.cnf
.SILENT:

run:
	python3 main.py --heuristics $(HEURISTICS) --filename $(FILENAME)

dynamic:
	make run HEURISTICS=DynamicLargestIndividualSumSolver FILENAME=$(FILENAME)

jeroslow:
	make run HEURISTICS=JeroslowWangOneSidedSolver FILENAME=$(FILENAME)

random:
	make run HEURISTICS=RandomHeuristicsSolver FILENAME=$(FILENAME)

twoclause:
	make run HEURISTICS=TwoClauseHeuristicSolver FILENAME=$(FILENAME)

clean:
	rm -f *.pyc
	rm -rf __pycache__

help:
	@echo "Usage:"
	@echo "  make <heuristic> FILENAME=<filename>"
	@echo "Heuristic shortcuts:"
	@echo "  dynamic   - DynamicLargestIndividualSumSolver"
	@echo "  jeroslow  - JeroslowWangOneSidedSolver"
	@echo "  random    - RandomHeuristicsSolver"
	@echo "  twoclause - TwoClauseHeuristicSolver"
	@echo "Example:"
	@echo "  make random FILENAME=test.cnf"
