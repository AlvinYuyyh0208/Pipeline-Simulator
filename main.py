# Helper function to parse binary instructions into Instruction objects
def parse_binary_instruction(binary_string):
    opcode = binary_string[:6]  # Get the opcode from the binary string
    # Decoding the opcode to identify instruction type and parameters
    # This is a simplified placeholder; you would need a complete mapping for each opcode
    if opcode == "000000":  # This is usually the R-type format
        # Parse binary string into components for R-type instructions
        # Example: opcode (6), rs (5), rt (5), rd (5), shamt (5), funct (6)
        funct = binary_string[26:]  # Last 6 bits for R-type instructions
        # Assuming specific functionality based on funct field as an example
        if funct == "100000":  # 'add' operation
            return Instruction(name="Add", src1="R1", src2="R2", dest="R3", opcode="add")
    elif opcode == "001000":  # This could be an I-type 'addi' instruction
        return Instruction(name="Addi", src1="R1", dest="R2", opcode="addi")
    # Continue parsing for other opcodes (load, store, branch, etc.)
    return Instruction(name="NOP")  # Default to NOP if unknown


# Load instructions from the file and parse them
def load_instructions_from_file(file_path):
    instructions = []
    with open(file_path, 'r') as file:
        for line in file:
            binary_string = line.strip()
            if binary_string:  # Only parse non-empty lines
                instruction = parse_binary_instruction(binary_string)
                instructions.append(instruction)
    return instructions


# forwarding
class Instruction:
    def __init__(self, name="NOP", src1=None, src2=None, dest=None, opcode=None):
        self.name = name
        self.src1 = src1  # Source register 1
        self.src2 = src2  # Source register 2
        self.dest = dest  # Destination register
        self.opcode = opcode  # Operation type (e.g., load, store, add, sub)


class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.instruction = Instruction()  # Default to NOP

    def set_instruction(self, instruction):
        self.instruction = instruction

    def clear(self):
        self.instruction = Instruction(name="NOP")


class MIPSPipelineSimulator:
    def __init__(self):
        self.stages = {
            "IF": PipelineStage("IF"),
            "IS": PipelineStage("IS"),
            "ID": PipelineStage("ID"),
            "RF": PipelineStage("RF"),
            "EX": PipelineStage("EX"),
            "DF": PipelineStage("DF"),
            "DS": PipelineStage("DS"),
            "WB": PipelineStage("WB")
        }
        self.clock_cycle = 0
        self.instructions = []
        self.stall_count = {"Loads": 0, "Branches": 0, "Other": 0}
        self.forwarding_count = {"EX/DF -> RF/EX": 0, "DF/DS -> EX/DF": 0, "DF/DS -> RF/EX": 0, "DS/WB -> EX/DF": 0,
                                 "DS/WB -> RF/EX": 0}
        self.registers = {f"R{i}": 0 for i in range(32)}  # Integer registers
        self.data_memory = {i: 0 for i in range(600, 640, 4)}  # Sample memory addresses
        self.pipeline_registers = {
            "IF/IS.NPC": 496, "IS/ID.IR": 0, "RF/EX.A": 0, "RF/EX.B": 0,
            "EX/DF.ALUout": 0, "EX/DF.B": 0, "DS/WB.ALUout-LMD": 0
        }

    def load_instructions(self, instructions):
        self.instructions = instructions

    def advance_pipeline(self):
        # Move instructions to the next stage in reverse order to avoid overwriting
        self.stages["WB"].set_instruction(self.stages["DS"].instruction)
        self.stages["DS"].set_instruction(self.stages["DF"].instruction)
        self.stages["DF"].set_instruction(self.stages["EX"].instruction)
        self.stages["EX"].set_instruction(self.stages["RF"].instruction)
        self.stages["RF"].set_instruction(self.stages["ID"].instruction)
        self.stages["ID"].set_instruction(self.stages["IS"].instruction)
        self.stages["IS"].set_instruction(self.stages["IF"].instruction)

        # Fetch the next instruction if available
        if self.instructions:
            next_instr = self.instructions.pop(0)
            self.stages["IF"].set_instruction(next_instr)
            self.pipeline_registers["IF/IS.NPC"] += 4  # Increment PC for next instruction
        else:
            self.stages["IF"].clear()

    def run_cycle(self):
        print(f"\n***** Cycle #{self.clock_cycle}***********************************************")
        print(f"Current PC = {self.pipeline_registers['IF/IS.NPC']}:")

        # Display pipeline status
        print("Pipeline Status:")
        for stage_name, stage in self.stages.items():
            instr_name = stage.instruction.name if stage.instruction else "<unknown>"
            print(f"* {stage_name} : {instr_name}")

        # Display stall and forwarding information (placeholder logic)
        print("Stall Instruction: (none)")
        print("Forwarding:")
        print("Detected: (none)")
        print("Forwarded:")
        for key in self.forwarding_count.keys():
            print(f"* {key} : (none)")

        # Display pipeline registers
        print("Pipeline Registers:")
        for reg, value in self.pipeline_registers.items():
            print(f"* {reg} : {value}")

        # Display integer registers
        print("Integer registers:")
        for i in range(0, 32, 4):
            reg_values = " ".join([f"R{i + j} {self.registers[f'R{i + j}']}" for j in range(4)])
            print(reg_values)

        # Display data memory contents
        print("Data memory:")
        for addr, value in self.data_memory.items():
            print(f"{addr}: {value}")

        # Display total stalls and forwarding counts
        print("Total Stalls:")
        for key, count in self.stall_count.items():
            print(f"* {key} : {count}")
        print("Total Forwardings:")
        for key, count in self.forwarding_count.items():
            print(f"* {key} : {count}")

        # Advance pipeline stages
        self.advance_pipeline()
        self.clock_cycle += 1

    def run(self, max_cycles=40):
        while self.clock_cycle < max_cycles:
            self.run_cycle()



# Initialize and run the simulator
simulator = MIPSPipelineSimulator()
instructions = load_instructions_from_file("fibonacci_input.txt")
simulator.load_instructions(instructions)
simulator.run(max_cycles=40)
