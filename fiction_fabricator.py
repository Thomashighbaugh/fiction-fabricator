from src.write_novel import write_novel
import g4f
# Introductory message featuring ASCII art
print(" _______ __        __   __                                    ")
print("|    ___|__|.----.|  |_|__|.-----.-----.                      ")
print("|    ___|  ||  __||   _|  ||  _  |     |                      ")
print("|___|   |__||____||____|__||_____|__|__|                      ")
print(" _______         __          __              __               ")
print("|    ___|.---.-.|  |--.----.|__|.----.---.-.|  |_.-----.----. ")
print("|    ___||  _  ||  _  |   _||  ||  __|  _  ||   _|  _  |   _| ")
print("|___|    |___._||_____|__|  |__||____|___._||____|_____|__|   ")
print("                                                              ")
print("by Thomas Leon Highbaugh\n\n\n")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")


def main():
    # g4f settings arranged early
    g4f.debug.logging = False
    g4f.debug.version_check = False

    """
    Entry point for the Fiction Fabricator tool.
    """


    write_novel()


if __name__ == "__main__":
    main()
