run:
	@ $(MAKE) clean
# 	@clear
	@echo "\033[1;33m"
# 	@echo " ~╚¥╝~   ╠═▄▄═╣   ╠═¤¤═╣   ╠¤¤╣   ╠-¥-╣  ╠--▄▄--╣"
	@echo ""
	@echo "███████╗ ██╗      ██╗    ██╗      ██╗ ███╗   ██╗"
	@echo "██╔════╝ ██║       ██║  ██╔╝      ██║ ████╗  ██║"
	@echo "█████╗   ██║       ╚██╗██╔╝  ▄▄▄  ██║ ██╔██╗ ██║"
	@echo "██╔══╝   ██║         ╚██╔╝   ▀▀▀  ██║ ██║╚██╗██║"
	@echo "██║      ███████╗     ██║         ██║ ██║ ╚████║""      ~╚¥╝~     ╠═▄▄═╣     ╠═¤¤═╣     ╠¤¤╣     ╠-¥-╣    ╠--▄▄--╣"
	@echo "╚═╝      ╚══════╝     ╚═╝         ╚═╝ ╚═╝  ╚═══╝"
	@echo "\n"
	@echo "\033[1;32m"
	@ python3 fly_in.py prueba.txt
	@echo "\033[31m"
	@echo "\nEND OF PROGRAM - SEE YOU SOON!"

clean:
	@clear
# 	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
# 	@rm -rf .mypy_cache dist build *.egg-info