import py_trees
import threading
import time

# Global variable to track pause state
paused = False

def description() -> str:
    """
    Print description and usage information about the program.

    Returns:
        the program description string
    """
    content = (
        "Testing out manual progressing tick in decision tree with simulated pauses.\n"
    )

    if py_trees.console.has_colours:
        banner_line = py_trees.console.green + "*" * 79 + "\n" + py_trees.console.reset
        s = banner_line
        s += py_trees.console.bold_white + "Selectors".center(79) + "\n" + py_trees.console.reset
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += banner_line
    else:
        s = content
    return s

class InterruptibleNode(py_trees.behaviour.Behaviour):
    def __init__(self, name: str):
        super().__init__(name)
        self.status = py_trees.common.Status.RUNNING

    def update(self) -> py_trees.common.Status:
        if paused:
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.RUNNING

def create_root() -> py_trees.behaviour.Behaviour:
    """
    Create the root behaviour and its subtree.

    Returns:
        the root behaviour
    """
    root = py_trees.composites.Selector(name="Selector", memory=False)
    
    interruptible_node1 = InterruptibleNode(name="Interruptible Node 1")
    always_running1 = py_trees.behaviours.Running(name="Running 1")
    interruptible_node2 = InterruptibleNode(name="Interruptible Node 2")
    always_running2 = py_trees.behaviours.Running(name="Running 2")

    root.add_children([interruptible_node1, always_running1, interruptible_node2, always_running2])
    
    return root

def toggle_pause():
    global paused
    while True:
        input("Press Enter to toggle pause: ")
        paused = not paused
        if paused:
            print("Tree is now paused.")
        else:
            print("Tree is now running.")

def main() -> None:
    """Entry point for the demo script."""
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    root = create_root()
    behaviour_tree = py_trees.trees.BehaviourTree(root)

    # Start the pause toggling in a separate thread
    thread = threading.Thread(target=toggle_pause)
    thread.daemon = True
    thread.start()

    root.setup_with_descendants()

    i = 1
    try:
        while True:
            if not paused:
                print("\n--------- Tick {0} ---------\n".format(i))
                behaviour_tree.tick()
                print(py_trees.display.unicode_tree(root=root, show_status=True))
                i += 1
            time.sleep(1.0)  # Slow down the ticking process
    except KeyboardInterrupt:
        print("Execution interrupted by user.")

if __name__ == "__main__":
    main()
