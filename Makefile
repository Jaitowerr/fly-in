.PHONY: install run debug lint lint-strict clean

ENTRY_SCRIPT ?= fly_in.py
ARGS ?= 'prueba.txt'

run:
	@ $(MAKE) clean
# 	@clear
	@echo "\033[1;33m"
	@echo ""
	@echo "███████╗ ██╗      ██╗    ██╗      ██╗ ███╗   ██╗"
	@echo "██╔════╝ ██║       ██║  ██╔╝      ██║ ████╗  ██║"
	@echo "█████╗   ██║       ╚██╗██╔╝  ▄▄▄  ██║ ██╔██╗ ██║"
	@echo "██╔══╝   ██║         ╚██╔╝   ▀▀▀  ██║ ██║╚██╗██║"
	@echo "██║      ███████╗     ██║         ██║ ██║ ╚████║""      ~╚¥╝~     ╠═▄▄═╣     ╠═¤¤═╣     ╠¤¤╣     ╠-¥-╣    ╠--▄▄--╣"
	@echo "╚═╝      ╚══════╝     ╚═╝         ╚═╝ ╚═╝  ╚═══╝"
	@echo "\n"
	@ $(MAKE) install
# 	@echo "\033[1;32m"
	@echo "\033[1;33m"
	@poetry run python3 $(ENTRY_SCRIPT) $(ARGS)
	@echo "\033[31m"
	@echo "\nEND OF PROGRAM - SEE YOU SOON!"


install:
	@poetry install --no-interaction

debug: install
	@poetry run python3 -m pdb $(ENTRY_SCRIPT) $(ARGS)

lint: install
	@poetry run flake8 .
	@poetry run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict: install
	@poetry run flake8 .
	@poetry run mypy --strict .

clean:
	@clear
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	@rm -rf .mypy_cache dist build *.egg-info















# run:
# 	@ $(MAKE) clean
# # 	@clear
# 	@echo "\033[1;33m"
# # 	@echo " ~╚¥╝~   ╠═▄▄═╣   ╠═¤¤═╣   ╠¤¤╣   ╠-¥-╣  ╠--▄▄--╣"
# 	@echo ""
# 	@echo "███████╗ ██╗      ██╗    ██╗      ██╗ ███╗   ██╗"
# 	@echo "██╔════╝ ██║       ██║  ██╔╝      ██║ ████╗  ██║"
# 	@echo "█████╗   ██║       ╚██╗██╔╝  ▄▄▄  ██║ ██╔██╗ ██║"
# 	@echo "██╔══╝   ██║         ╚██╔╝   ▀▀▀  ██║ ██║╚██╗██║"
# 	@echo "██║      ███████╗     ██║         ██║ ██║ ╚████║""      ~╚¥╝~     ╠═▄▄═╣     ╠═¤¤═╣     ╠¤¤╣     ╠-¥-╣    ╠--▄▄--╣"
# 	@echo "╚═╝      ╚══════╝     ╚═╝         ╚═╝ ╚═╝  ╚═══╝"
# 	@echo "\n"
# 	@echo "\033[1;32m"
# 	@ python3 fly_in.py prueba.txt
# 	@echo "\033[31m"
# 	@echo "\nEND OF PROGRAM - SEE YOU SOON!"

# clean:
# 	@clear
# # 	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
# # 	@rm -rf .mypy_cache dist build *.egg-info