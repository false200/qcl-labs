"""Split the original lab into documented, independently runnable notebooks.

Run from the repository root with: uv run python scripts/split_notebook.py
The original Lab1.ipynb is only read. Generated notebooks have cleared outputs;
rerunning this script replaces the six generated notebooks, including edits.
"""

from copy import deepcopy
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]

# Cell indices refer to the original combined notebook (zero based).
LABS = [
    (
        "01_quantum_circuit_basics.ipynb",
        "Quantum Circuit Basics and Simulation",
        "Build circuits with Hadamard and Pauli-X gates, measure qubits, run shot-based simulations, and compare sampled counts with exact statevector probabilities.",
        [],
        [
            (0, "Drawing and measuring a circuit", "H creates an equal superposition; X exchanges its amplitudes. The original circuit already has a classical bit, so `measure_all()` adds another register. The unused original bit stays zero."),
            (1, "Sampling a single-qubit superposition", "Expect approximately equal counts for `0` and `1` over 1,000 shots. Sampling counts vary between runs."),
            (2, "Two qubits in superposition", "Both qubits have equal measurement probabilities, so `00`, `01`, `10`, and `11` each occur with probability 1/4."),
            (3, "Operating on one of two qubits", "Only q0 is changed. Expect `00` and `01` with approximately equal counts; q1 remains zero."),
            (4, "Statevectors and measurement probabilities", "H on q0 and X on q1 produce outcomes `10` and `11`, each with probability 1/2. Compute the statevector before adding measurements."),
        ],
    ),
    (
        "02_quantum_gates_and_statevectors.ipynb",
        "Quantum Gates and Statevectors",
        "Explore phase gates, controlled-Z, SWAP, and controlled-SWAP using exact statevectors and circuit diagrams.",
        ["from qiskit import QuantumCircuit", "from qiskit.quantum_info import Statevector"],
        [
            (5, "Converting phase into a bit flip: H-Z-H", "The identity HZH = X maps the initial |0> state to |1>. All ideal measurement shots return `1`."),
            (6, "Four T gates", "T applied four times equals Z. On the prepared |1> state the result is -|1>; the global phase does not change measurement probabilities."),
            (7, "Controlled-Z", "CZ changes the sign of |11>. For this basis-state input the sign is a global phase, so the probability of `11` remains 1."),
            (8, "SWAP", "The initial displayed state `01` becomes `10` when q0 and q1 are exchanged."),
            (9, "Controlled-SWAP (Fredkin gate)", "With q0 set to 1, exchange q1 and q2. In q2q1q0 order the initial `101` becomes `011`."),
        ],
    ),
    (
        "03_quantum_full_adder.ipynb",
        "Quantum Full Adder",
        "Construct a reversible full adder with CNOT and Toffoli gates. Inputs are q0 = A, q1 = B, and q2 = carry-in; outputs are q3 = sum and q4 = carry-out. The circuit restores the input B after using it temporarily.",
        [],
        [
            (10, "Adding a fixed input: 1 + 1 + 1", "The sum is A XOR B XOR carry-in. Carry-out is (A AND B) XOR ((A XOR B) AND carry-in). This example measures only the outputs, with strings ordered `carry sum`; expect `11`."),
            (11, "All input combinations in superposition", "Hadamard gates prepare all eight inputs with equal amplitudes. All five qubits are measured, so each string is ordered `carry sum carry-in B A`. Each shot reveals one valid input/output combination."),
        ],
    ),
    (
        "04_deutsch_algorithm.ipynb",
        "Deutsch's Algorithm",
        "Classify a one-bit Boolean function as constant or balanced using one quantum oracle call. Prepare the auxiliary qubit in |-> so the oracle encodes the function as a phase.",
        [],
        [
            (12, "Classifying one oracle", "After the final Hadamard, measurement `0` means constant and `1` means balanced. This example uses `balanced01`, meaning f(x) = x. The original call used the unrecognized name `balanced1`; it is corrected here."),
            (13, "Comparing all four Boolean functions", "`constant0` and `constant1` always return 0 and 1, respectively; `balanced01` implements x and `balanced10` implements 1 XOR x. Expect measurement `0` for both constant functions and `1` for both balanced functions."),
        ],
    ),
    (
        "05_deutsch_jozsa_algorithm.ipynb",
        "Deutsch-Jozsa Algorithm",
        "Extend constant-versus-balanced classification to four input qubits. The algorithm assumes the function is promised to be either constant or balanced.",
        ["from qiskit import QuantumCircuit, transpile", "from qiskit_aer import Aer", "from qiskit.visualization import plot_histogram"],
        [
            (14, "Classifying a randomly selected oracle", "The balanced oracle computes the parity of the input bits. An ideal constant oracle returns `0000`; this particular parity oracle returns `1111`. The oracle is chosen randomly on each run."),
        ],
    ),
    (
        "06_bernstein_vazirani_algorithm.ipynb",
        "Bernstein-Vazirani Algorithm",
        "Recover a hidden four-bit string with one quantum oracle call. The oracle computes the bitwise inner product of the input and hidden string, modulo 2.",
        ["import random", "from qiskit import QuantumCircuit, transpile", "from qiskit_aer import Aer", "from qiskit.visualization import plot_histogram"],
        [
            (15, "Recovering the hidden string", "A CNOT targets the auxiliary qubit for each 1 in the hidden string. Reversing the string maps its rightmost bit to q0. The measured result should exactly match the generated hidden string, including leading zeros."),
        ],
    ),
]


def updated_source(index, source):
    """Retain the original code/comments, with small documented corrections."""
    if index == 11:
        source = source.replace(
            "# Create circuit: 5 qubits, 2 classical bits",
            "# Create circuit: 5 qubits; measure_all() later adds 5 classical bits",
        ).replace("# Measure Sum and Carry", "# Measure inputs, Sum, and Carry")
    if index in (12, 13):
        source = source.replace(
            "def oracle(x):\n    qc = QuantumCircuit(2)",
            'def oracle(x):\n'
            '    # Reject unknown names instead of silently using the identity oracle.\n'
            '    if x not in {"constant0", "constant1", "balanced01", "balanced10"}:\n'
            '        raise ValueError(f"Unknown oracle type: {x}")\n'
            '    qc = QuantumCircuit(2)',
        ).replace('algo("balanced1")', 'algo("balanced01")')
    if index == 14:
        source = source.replace(
            "choice = random.choice(types)",
            'choice = random.choice(types)\nprint("Selected oracle:", choice)',
        )
    if index == 15:
        source = source.replace(
            "qc.cx(i , n)",
            "qc.cx(i , m)  # The auxiliary index comes from this oracle's string length.",
        ).replace("print(maxa)", 'print("Hidden string:", s)\nprint("Recovered string:", maxa)')
    return source


def main():
    original = nbformat.read(ROOT / "Lab1.ipynb", as_version=4)
    if len(original.cells) != 16 or any(c.cell_type != "code" for c in original.cells):
        raise ValueError("Expected the original notebook's 16 code cells; review the split mapping.")

    destination = ROOT / "notebooks"
    destination.mkdir(exist_ok=True)
    for filename, title, objective, imports, sections in LABS:
        notebook = nbformat.v4.new_notebook(metadata=deepcopy(original.metadata))
        notebook.metadata.kernelspec = {
            "display_name": "Python 3", "language": "python", "name": "python3"
        }
        notebook.cells = [nbformat.v4.new_markdown_cell(
            f"# {title}\n\n{objective}\n\n"
            "Run the cells from top to bottom in a fresh Python kernel. "
            "See the [repository README](../README.md) for environment setup.\n\n"
            "**Bit ordering:** Qiskit displays bit strings with the highest-index bit "
            "on the left and bit 0 on the right. Ideal simulator results are used here; "
            "shot counts can fluctuate when several outcomes have nonzero probability."
        )]
        if imports:
            notebook.cells.append(nbformat.v4.new_code_cell(
                "# Imports needed to run this notebook independently.\n" + "\n".join(imports)
            ))
        for index, heading, explanation in sections:
            notebook.cells.append(nbformat.v4.new_markdown_cell(f"## {heading}\n\n{explanation}"))
            cell = deepcopy(original.cells[index])
            cell.source = updated_source(index, cell.source)
            cell.outputs = []
            cell.execution_count = None
            notebook.cells.append(cell)
        for index, cell in enumerate(notebook.cells):
            # Stable identifiers keep repeated generation from creating noisy diffs.
            cell.id = f"{filename[:2]}-cell-{index:02d}"
        nbformat.validate(notebook)
        nbformat.write(notebook, destination / filename)
        print(f"Created notebooks/{filename}")


if __name__ == "__main__":
    main()
