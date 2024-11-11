# error
# pipeline register should +4
# instruction in pipeline stage should move to next stage

def parse_instruction(word):
    opcode = word & 0x7f  # [6,0]
    rd = (word >> 7) & 0x1f  # [11,7]
    funct3 = (word >> 12) & 0x7  # [14,12]
    rs1 = (word >> 15) & 0x1f  # [19,15]
    rs2 = (word >> 20) & 0x1f  # [24,20]
    funct7 = (word >> 25) & 0x7f  # [31,25]

    imme_i = (word >> 20) & 0xfff  # [31,20]
    imme_s = ((word >> 25) & 0x7f) << 5 | ((word >> 7) & 0x1f)
    imme_b = ((word >> 31) & 0x1) << 12 | ((word >> 25) & 0x3f) << 5 | ((word >> 8) & 0xf) << 1 | (
            (word >> 7) & 0x1) << 11
    imme_u = ((word >> 12) & 0xfffff) << 12
    imme_j = ((word >> 31) & 0x1) << 20 | ((word >> 21) & 0x3ff) << 1 | ((word >> 20) & 0x1) << 11 | (
            (word >> 12) & 0xff) << 12

    # sign extend
    if imme_i & (1 << 11):
        imme_i |= ~0xFFF

    if imme_s & (1 << 11):
        imme_s |= ~0xFFF

    if imme_b & (1 << 12):
        imme_b |= ~0x1FFF

    if imme_j & (1 << 20):
        imme_j |= ~0xFFFFF

    return opcode, rd, funct3, rs1, rs2, funct7, imme_i, imme_s, imme_b, imme_u, imme_j


def disassemble_instruction(opcode, rd, funct3, rs1, rs2, funct7, imme_i, imme_s, imme_b, imme_u, imme_j):
    # R-type instruction
    if opcode == 51:
        if funct7 == 0 and funct3 == 0:
            return f"ADD x{rd}, x{rs1}, x{rs2}"
        elif funct7 == 32 and funct3 == 0:
            return f"SUB x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 1 and funct7 == 0:
            return f"SLL x{rd}, x{rs1}, {rs2}"
        elif funct3 == 5 and funct7 == 0:
            return f"SRL x{rd}, x{rs1}, {rs2}"
        elif funct3 == 5 and funct7 == 32:
            return f"SRA x{rd}, x{rs1}, {rs2}"
        elif funct3 == 7 and funct7 == 0:
            return f"AND x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 6 and funct7 == 0:
            return f"OR x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 4 and funct7 == 0:
            return f"XOR x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 2 and funct7 == 0:
            return f"SLT x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 3 and funct7 == 0:
            return f"SLTU  x{rd}, x{rs1}, x{rs2}"


    # I-type instruction
    elif opcode == 19:
        if funct3 == 0:
            return f"ADDI x{rd}, x{rs1}, {imme_i}"
        elif funct3 == 7:
            return f"ANDI x{rd}, x{rs1}, {imme_i}"
        elif funct3 == 6:
            return f"ORI x{rd}, x{rs1}, {imme_i}"
        elif funct3 == 4:
            return f"XORI x{rd}, x{rs1}, {imme_i}"
        elif funct3 == 2:
            return f"SLTI x{rd}, x{rs1}, {imme_i}"

    # Load/Store instructions
    elif opcode == 3:
        if funct3 == 2:
            return f"LW x{rd}, {imme_i}(x{rs1})"
    elif opcode == 35:
        if funct3 == 2:
            return f"SW x{rs2}, {imme_s}(x{rs1})"

    # Branch instructions
    elif opcode == 99:
        if funct3 == 0:
            return f"BEQ x{rs1}, x{rs2}, {imme_b}"
        elif funct3 == 1:
            return f"BNE x{rs1}, x{rs2}, {imme_b}"
        elif funct3 == 4:
            return f"BLT x{rs1}, x{rs2}, {imme_b}"
        elif funct3 == 5:
            return f"BGE x{rs1}, x{rs2}, {imme_b}"
        elif funct3 == 6:
            return f"BLTU x{rs1}, x{rs2}, {imme_b}"
        elif funct3 == 7:
            return f"BGEU x{rs1}, x{rs2}, {imme_b}"

    # Jump instructions
    elif opcode == 111:
        return f"JAL x{rd}, {imme_j}"
    elif opcode == 103:
        return f"JALR x{rd}, x{rs1}, {imme_i}"

    return "0"


def format_instruction_groups(binary_str):
    groups = [binary_str[:6], binary_str[6:12], binary_str[12:17], binary_str[17:20], binary_str[20:25],
              binary_str[25:]]
    return ' '.join(groups)


# New function to parse and load instructions into the simulator
def load_and_disassemble_instructions(input_filename):
    instructions = []
    current_address = 496

    with open(input_filename, 'r') as infile:
        for line in infile:
            word = int(line.strip(), 2)
            # Parse and disassemble the binary instruction
            opcode, rd, funct3, rs1, rs2, funct7, imme_i, imme_s, imme_b, imme_u, imme_j = parse_instruction(word)
            instruction_str = disassemble_instruction(opcode, rd, funct3, rs1, rs2, funct7, imme_i, imme_s, imme_b,
                                                      imme_u, imme_j)
            binary_str = format_instruction_groups(line.strip())

            # Create an Instruction object with disassembled information
            instruction = Instruction(
                name=instruction_str,
                src1=f"x{rs1}" if rs1 is not None else None,
                src2=f"x{rs2}" if rs2 is not None else None,
                dest=f"x{rd}" if rd is not None else None,
                opcode=opcode
            )
            instructions.append(instruction)

            current_address += 4
            if current_address == 700:
                break  # Stop at address 700 as specified

    return instructions


# disassemble('fibonacci_input.txt', 'output.txt')

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
instructions = load_and_disassemble_instructions("fibonacci_input.txt")
simulator.load_instructions(instructions)
simulator.run(max_cycles=40)
