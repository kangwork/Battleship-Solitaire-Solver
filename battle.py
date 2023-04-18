import sys
from copy import copy, deepcopy

input_filename = sys.argv[1]
output_filename = sys.argv[2]

H = 0
V = 1
L = 'L'
R = 'R'
M = 'M'
S = 'S'
T = 'T'
B = 'B'
W = 'W'
lvl_counting = [0]

AllConstraints = dict()
preassigned = {W: set(), S: set(), M: set(),
               L: set(), R: set(),
               T: set(), B: set()}
aroundpreassigned = {S: set(), M: set(),
                     L: set(), R: set(),
                     T: set(), B: set()}

input_string = []
row_constraint = {}  # top to bottom
col_constraint = {}  # left to right

with open(input_filename, 'r') as input_file:
    mylist = input_file.readlines()

string_row = mylist[0].rstrip()
n = len(string_row)
string_col = mylist[1].rstrip()
string_ships = mylist[2].rstrip()

counting = [0]
KINDtoHASH = {1: set(), 2: set(), 3: set(), 4: set()}
HASHtoKIND = {}
HASHtoSHIP = dict()
ALL_HASHES = set()  # equivalent to set(HASHtoSHIP), but just to make it faster.


class Level(object):
    """ Level is a class that holds a current domain of this level.

        - variables maps hash(ship) to ship object.
        - curdoms maps to hash(ship) to its current domain, in both
            orientations(H,V) combined."""
    def __init__(self, row_dict, col_dict, CurDoms=None):
        if CurDoms is None:
            self.CurDoms = dict()
            for variable_hash in HASHtoSHIP:
                self.CurDoms[variable_hash] = copy(HASHtoSHIP[variable_hash].Dom)
        else:
            self.CurDoms = copy(CurDoms)  # inherit from parent level
        self.row_dict = row_dict
        self.col_dict = col_dict

    def remove_d_from_T(self, T: int, d: tuple):
        self.CurDoms[T].remove(d)

    def pick_unassigned_variable(self, unassigned: set):
        """Precondition:
            unassigned contains at least one element."""
        mrv = 0
        mrv_value = float('inf')
        
        for var in unassigned:
            size = len(self.CurDoms[var])
            if size < mrv_value or (size <= mrv_value+5 and HASHtoKIND[var] > HASHtoKIND[mrv]):
                mrv = var
                mrv_value = size
     
        return mrv
        

class Ship(object):
    """
    VARIABLE DESIGN:
    EACH SHIP IS A VARIABLE.
    THERE ARE k many SHIPS => THERE ARE k many VARIABLES.
    2 possible domains.

    ship_kind = {1, 2, 3, 4}
        1: submarine
        2: destroyer
        3: cruiser
        4: battleship

    occupied = {all cells (10*i + j) where 0 <= i, j < n}
        all occupied cells of the ship
        can be exactly ship_kind 만큼의 cells
        eg. for submarine,(ship_kind=1)

    head = Occupied position that is either L, T, or S(for submarine).
    tail = Occupied position that is either R, B, or S.

        """

    def __init__(self, constraints_to_consider: set):
        """
        th_ship = (1,..., total_ships)
        Recall:
        Dom is where occupied pair tuple can be located.
        Submarine is where there is only one H,
        remainders are H or V.
        maps orientation to possible domain
        """
        counting[0] += 1
        self.hashnum = counting[0]
        self.Dom = set()
        self.constraints_to_consider = constraints_to_consider


    def add_constraints_to_consider(self, constraint_hash: int):
        """This is for adding constraints to consider, especially the
        PersonalSpace Constraints which pairs all the other variables to self.
        """
        self.constraints_to_consider.add(constraint_hash)

    def add_possible_pos(self, ori_poss: tuple):
        """
        :param ori_poss: eg. (H, (0,)), (H, (0, 1)), (V, (10, 20, 30))
        :return: nothing
        """
        self.Dom.add(ori_poss)

    def __hash__(self) -> int:
        return self.hashnum


class Submarine(Ship):
    def __init__(self):
        super().__init__(set())


class Destroyer(Ship):
    def __init__(self):
        constraint_to_consider = {3000+i for i in mutablepreassigned[T]}.union(
            {3000+i for i in mutablepreassigned[R]}).union(
            {3000+i for i in mutablepreassigned[B]}).union(3000+i for i in shouldbeinOneoftheDorC)
        super().__init__(constraint_to_consider)


class Cruiser(Ship):
    def __init__(self):
        constraint_to_consider = {3000+i for i in mutablepreassigned[T]}.union(
            {3000+i for i in mutablepreassigned[R]}).union(
            {3000+i for i in mutablepreassigned[B]}).union(
            {3000+i for i in mutablepreassigned[M]}).union(
            3000+i for i in shouldbeinOneoftheDorC)
        # Finding possible head position by for first
        # the num of middle+tailpieces that needs to be followed by the head
        super().__init__(constraint_to_consider)


class BattleShip(Ship):
    def __init__(self):
        constraint_to_consider = {3000+i for i in mutablepreassigned[T]}.union(
            {3000+i for i in mutablepreassigned[R]}).union(
            {3000+i for i in mutablepreassigned[B]}).union(
            {3000+i for i in mutablepreassigned[M]})

        # Finding possible head position by for first
        # the num of middle+tailpieces that needs to be followed by the head

        super().__init__(constraint_to_consider)


# -------------------------------Constraint-------------------------------------
class Constraint(object):
    def __init__(self, variables_to_consider):
        self.variables_to_consider = variables_to_consider


# ------------------------- ROW COLUMN Constraints------------------------------

class SRowConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        y = assignedPositionsTuple[0] // 10
        if level.row_dict[y] - 1 < 0:  # < ROW: H: my size V: my one unit size
            return False
        else:
            level.row_dict[y] -= 1  # Remove it as I am putting this piece
            return True

    def __str__(self):
        return f"Submarine {self.ship1} Row Constraint"

    def __hash__(self):
        return 1100 + self.ship1


class DRowConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        head_y = assignedPositionsTuple[0] // 10
        if assignedOrientation == H:  # horizontally placing, row. H+R size V+C size
            if level.row_dict[head_y] - 2 < 0:  # < ROW: H: my size V: my one unit size
                return False
            else:
                level.row_dict[head_y] -= 2  # Remove it as I am putting this piece
                return True
        else:  # Cuz vertically placing, and row. horizontally column.
            # -------------- Consider all pieces including header. ----------------------------
            tail_y = head_y + 1
            for piece_pos in assignedPositionsTuple:
                if level.row_dict[piece_pos//10] - 1 < 0:  # < ROW: H: whole piece size V: one unit size
                    return False
            # if fully_succeeded:  # In all piece case, head, tail
            level.row_dict[head_y] -= 1
            level.row_dict[tail_y] -= 1
            return True

    def __str__(self):
        return f"Submarine {self.ship1} Row Constraint"

    def __hash__(self):
        return 1200 + self.ship1


class CRowConstraint(Constraint):
    """one per EACH SHIP. Unary constraint"""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        head_y = assignedPositionsTuple[0] // 10
        if assignedOrientation == H:  # horizontally placing, row. H+R size V+C size
            if level.row_dict[head_y] - 3 < 0:  # < ROW: H: size V: unit size
                return False
            else:
                level.row_dict[head_y] -= 3  # Remove it as I am putting the piece
                return True
        else:  # vertically placing, and row여서. horizontally column도 한 개.
            # -------------- Consider all pieces including header. ----------------------------
            m_y = head_y + 1
            tail_y = head_y + 2
            for piece_pos in assignedPositionsTuple:
                if level.row_dict[piece_pos//10] - 1 < 0:  # < ROW: H: size V: one unit size
                    return False
            # if fully_succeeded:  # In all piece case, head and tail
            level.row_dict[head_y] -= 1
            level.row_dict[m_y] -= 1
            level.row_dict[tail_y] -= 1
            return True

    def __str__(self):
        return f"Cruiser {self.ship1} Row Constraint"

    def __hash__(self):
        return 1300 + self.ship1





class BRowConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        head_y = assignedPositionsTuple[0] // 10
        if assignedOrientation == H:  # horizontally placing, row. H+R 크기 V+C 크기
            if level.row_dict[head_y] - 4 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                return False
            else:
                level.row_dict[head_y] -= 4  # 이거 놓을 거니까 빼기.
                return True
        else:  # vertically placing, and row여서. horizontally column도 한 개.
            # -------------- 헤드 포함 모든 피쓰를 컨시더. ----------------------------
            # tail_y = assignedPositionsTuple[-1] // 10  # 고쳐 내가 계산할 수 있음
            m1_y = head_y + 1
            m2_y = head_y + 2
            tail_y = head_y + 3
            for piece_pos in assignedPositionsTuple:  # 고쳐 폴룹 꼭 안 돌려도 됨.
                if level.row_dict[piece_pos//10] - 1 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                    return False
            # if fully_succeeded:  # all piece로 이 경우 head, tail
            level.row_dict[head_y] -= 1
            level.row_dict[m1_y] -= 1
            level.row_dict[m2_y] -= 1
            level.row_dict[tail_y] -= 1
            return True

    def __str__(self):
        return f"Battleship {self.ship1} Row Constraint"

    def __hash__(self):
        return 1400 + self.ship1





#  -------------------------------- COL CONSTRAINT ----------------------------


class SColConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        x = assignedPositionsTuple[0] % 10
        if level.col_dict[x] - 1 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
            return False
        else:
            level.col_dict[x] -= 1  # 이거 놓을 거니까 빼기.
            return True

    def __str__(self):
        return f"Submarine {self.ship1} Col Constraint"

    def __hash__(self):
        return 2100 + self.ship1



class DColConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        head_x = assignedPositionsTuple[0] % 10
        if assignedOrientation == V:  # horizontally placing, row. H+R 크기 V+C 크기
            if level.col_dict[head_x] - 2 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                return False
            else:
                level.col_dict[head_x] -= 2  # 이거 놓을 거니까 빼기.
                return True
        else:  # vertically placing, and row여서. horizontally column도 한 개.
            # -------------- 헤드 포함 모든 피쓰를 컨시더. ----------------------------
            # tail_y = assignedPositionsTuple[-1] // 10  # 고쳐 내가 계산할 수 있음
            tail_x = head_x + 1
            for piece_pos in assignedPositionsTuple:  # 고쳐 폴룹 꼭 안 돌려도 됨.
                if level.col_dict[piece_pos % 10] - 1 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                    return False
            # if fully_succeeded:  # all piece로 이 경우 head, tail
            level.col_dict[head_x] -= 1
            level.col_dict[tail_x] -= 1
            return True

    def __str__(self):
        return f"Destroyer {self.ship1} Col Constraint"

    def __hash__(self):
        return 2200 + self.ship1




class CColConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        head_x = assignedPositionsTuple[0] % 10
        if assignedOrientation == V:  # horizontally placing, row. H+R 크기 V+C 크기
            if level.col_dict[head_x] - 3 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                return False
            else:
                level.col_dict[head_x] -= 3  # 이거 놓을 거니까 빼기.
                return True
        else:  # vertically placing, and row여서. horizontally column도 한 개.
            # -------------- 헤드 포함 모든 피쓰를 컨시더. ----------------------------
            # tail_y = assignedPositionsTuple[-1] // 10  # 고쳐 내가 계산할 수 있음
            m_x = head_x + 1
            tail_x = head_x + 2
            for piece_pos in assignedPositionsTuple:  # 고쳐 폴룹 꼭 안 돌려도 됨.
                if level.col_dict[piece_pos % 10] - 1 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                    return False
            # if fully_succeeded:  # all piece로 이 경우 head, tail
            level.col_dict[head_x] -= 1
            level.col_dict[m_x] -= 1
            level.col_dict[tail_x] -= 1
            return True

    def __str__(self):
        return f"Cruiser {self.ship1} Col Constraint"

    def __hash__(self):
        return 2300 + self.ship1





class BColConstraint(Constraint):
    """EACH SHIP 마다 하나씩. 유너리."""
    def __init__(self, ship1:int):
        self.ship1 = ship1
        super().__init__({ship1})

    def valid_with_these_values(self, variable_to_value: dict, level:Level):
        assignedOrientation, assignedPositionsTuple = variable_to_value[self.ship1]
        head_x = assignedPositionsTuple[0] % 10
        if assignedOrientation == V:  # horizontally placing, row. H+R 크기 V+C 크기
            if level.col_dict[head_x] - 4 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                return False
            else:
                level.col_dict[head_x] -= 4  # 이거 놓을 거니까 빼기.
                return True
        else:  # vertically placing, and row여서. horizontally column도 한 개.
            # -------------- 헤드 포함 모든 피쓰를 컨시더. ----------------------------
            # tail_y = assignedPositionsTuple[-1] // 10  # 고쳐 내가 계산할 수 있음
            m1_x = head_x + 1
            m2_x = head_x + 2
            tail_x = head_x + 3
            for piece_pos in assignedPositionsTuple:  # 고쳐 폴룹 꼭 안 돌려도 됨.
                if level.col_dict[piece_pos % 10] - 1 < 0:  # < ROW: H: 나의 크기 V: 나의 한 개
                    return False
            # if fully_succeeded:  # all piece로 이 경우 head, tail
            level.col_dict[head_x] -= 1
            level.col_dict[m1_x] -= 1
            level.col_dict[m2_x] -= 1
            level.col_dict[tail_x] -= 1
            return True

    def __str__(self):
        return f"Battleship {self.ship1} Col Constraint"

    def __hash__(self):
        return 2400 + self.ship1



# ----------------------PreAssignedPieceConstraint------------------------------
# ----------------- Create for each pre assigned S---------------------
# class PreAssignedS(Constraint):
#     """Create constraint for each pre-assigned submarine piece.
#         Cares about submarine only"""
#     def __init__(self, S_at: int):
#         self.S_at = S_at
#         variables_to_consider = KINDtoHASH[1]
#         super().__init__(variables_to_consider)
#
#     def valid_with_these_values(self, variable_to_value: dict):
#         found_one = False
#         for variable in self.variables_to_consider:
#             assignedOrientation, assignedPositionsTuple = variable_to_value[
#                 variable]
#             pos = assignedPositionsTuple[0]
#             if pos == self.S_at:
#                 found_one = True
#                 break
#         return found_one
#
#     def __str__(self):
#         return f"One of submarine should be preassigned S at {self.S_at}"
#
#     def __hash__(self):
#         return 3000 + self.S_at


# --------------------- for each pre assigned L piece --------------------------
class PreAssignedL(Constraint):
    """Create constraint for each pre-assigned L piece"""
    def __init__(self, L_at: int):
        self.L_at = L_at
        if L_at in shouldbeinOneoftheDorC:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3])
        else:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3]).union(KINDtoHASH[4])
        super().__init__(variables_to_consider)

    def valid_with_these_values(self, variable_to_value: dict, level):
        for variable in self.variables_to_consider:
            assignedOrientation, assignedPositionsTuple = variable_to_value[
                variable]
            if assignedOrientation != H:
                continue
            head = assignedPositionsTuple[0]
            # only need to consider horizontal head
            if head == self.L_at:
                return True
        return False

    def __str__(self):
        return f"One of long ships at {self.L_at}"

    def __hash__(self):
        return 3000 + self.L_at


class PreAssignedT(Constraint):
    """Create constraint for each pre-assigned T piece"""
    def __init__(self, T_at: int):
        self.T_at = T_at
        if T_at in shouldbeinOneoftheDorC:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3])
        else:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3]).union(KINDtoHASH[4])
        super().__init__(variables_to_consider)

    def valid_with_these_values(self, variable_to_value: dict, level):
        for variable in self.variables_to_consider:
            assignedOrientation, assignedPositionsTuple = variable_to_value[
                variable]
            if assignedOrientation != V:
                continue
            head = assignedPositionsTuple[0]  # only need to vertical head
            if head == self.T_at:
                return True
        return False

    def __str__(self):
        return f"One of long ships at {self.T_at}"

    def __hash__(self):
        return 3000 + self.T_at


class PreAssignedR(Constraint):
    """Create constraint for each pre-assigned R piece"""
    def __init__(self, R_at: int):
        self.R_at = R_at
        if R_at in shouldbeinOneoftheDorC:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3])
        else:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3]).union(KINDtoHASH[4])
        super().__init__(variables_to_consider)

    def valid_with_these_values(self, variable_to_value: dict, level):
        for variable in self.variables_to_consider:
            assignedOrientation, assignedPositionsTuple = variable_to_value[
                variable]
            if assignedOrientation != H:
                continue
            tail = assignedPositionsTuple[-1]  # only need to horizontal tail
            if tail == self.R_at:
                return True
        return False

    def __str__(self):
        return f"One of long ships at {self.R_at}"

    def __hash__(self):
        return 3000 + self.R_at


class PreAssignedB(Constraint):
    """Create constraint for each pre-assigned B piece"""
    def __init__(self, B_at: int):
        self.B_at = B_at
        if B_at in shouldbeinOneoftheDorC:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3])
        else:
            variables_to_consider = (KINDtoHASH[2]).union(KINDtoHASH[3]).union(KINDtoHASH[4])
        super().__init__(variables_to_consider)

    def valid_with_these_values(self, variable_to_value: dict, level):
        for variable in self.variables_to_consider:
            assignedOrientation, assignedPositionsTuple = variable_to_value[
                variable]
            if assignedOrientation != V:
                continue
            tail = assignedPositionsTuple[-1]  # only need to vertical tail
            if tail == self.B_at:
                return True
        return False

    def __str__(self):
        return f"One of long ships at {self.B_at}"

    def __hash__(self):
        return 3000 + self.B_at


class PreAssignedM(Constraint):
    """Create constraint for each pre-assigned M piece.
        One should have it in its middle, but NEVER in its head or tail."""
    def __init__(self, M_at: int):
        self.M_at = M_at
        variables_to_consider = (KINDtoHASH[3]).union(KINDtoHASH[4])
        super().__init__(variables_to_consider)

    def valid_with_these_values(self, variable_to_value: dict, level):
        for variable in self.variables_to_consider:
            assignedOrientation, assignedPositionsTuple = variable_to_value[
                variable]
            for pos in assignedPositionsTuple[1:-1]:
                # only need to consider nontailorhead
                if pos == self.M_at:
                    return True
        return False

    def __str__(self):
        return f"One of long ships at {self.M_at}"

    def __hash__(self):
        return 3000 + self.M_at


# --------------------- PERSONAL SPACE TOUCHING---------------------

class SubmarinePersonalSpace(Constraint):
    """SHIP1 = Submarine.
        Every ship pair(ship1 and ship2) do not
        invade another's personal space.
        i.e., every ship is surrounded by water at least one unit
        horizontally, vertically, diagonally."""
    def __init__(self, ship1: int, ship2: int):
        self.ship1 = ship1
        self.ship2 = ship2
        unique = "4"
        unique += str(ship1)
        unique += "101"
        unique += str(ship2)
        self.hashnum = int(unique)
        super().__init__({ship1, ship2})

    def valid_with_these_values(self, variable_to_value: dict, level):
        """Note, if ship1 is protected, ship2 is protected naturally.
        So we only need to check for one ship's personal space is protected."""
        # ship1, ship2 = self.variables_to_consider
        assignedOrientation1, assignedPositionsTuple1 = variable_to_value[
            self.ship1]
        assignedOrientation2, assignedPositionsTuple2 = variable_to_value[
            self.ship2]
        # HEAD personal space
        head = assignedPositionsTuple1[0]
        for ship2pos in assignedPositionsTuple2:
            if head % 10 != 0 and head-11 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            if head-10 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            if head % 10 != n-1 and head-9 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            if head % 10 != 0 and head-1 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            # if head == ship2pos:
            # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
            # return False
            if head % 10 != n-1 and head+1 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            if head % 10 != 0 and head+9 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            if head+10 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
            if head % 10 != n-1 and head+11 == ship2pos:
                # print(f"{assignedPositionsTuple1} Touching {assignedPositionsTuple2}")
                return False
        return True

    def __str__(self):
        return f"Submarine Touching {(ship2)}"
        # return f"{kind_determiner(ship1)} Touching {kind_determiner(ship2)}"

    def __hash__(self):
        return self.hashnum


class DestroyerPersonalSpace(Constraint):
    """SHIP1 = Submarine.
        Every ship pair(ship1 and ship2) do not
        invade another's personal space.
        i.e., every ship is surrounded by water at least one unit
        horizontally, vertically, diagonally."""
    def __init__(self, ship1: int, ship2: int):
        self.ship1 = ship1
        self.ship2 = ship2
        unique = "5"
        unique += str(ship1)
        unique += "101"
        unique += str(ship2)
        self.hashnum = int(unique)
        super().__init__({ship1, ship2})

    def valid_with_these_values(self, variable_to_value: dict, level):
        """Note, if ship1 is protected, ship2 is protected naturally.
        So we only need to check for one ship's personal space is protected."""
        # ship1, ship2 = self.variables_to_consider
        assignedOrientation1, assignedPositionsTuple1 = variable_to_value[
            self.ship1]
        assignedOrientation2, assignedPositionsTuple2 = variable_to_value[
            self.ship2]
        # HEAD personal space
        head = assignedPositionsTuple1[0]=
        personal_space = set()
        for pc1 in assignedPositionsTuple1:
            if pc1 % 10 != 0 and pc1 % 10 != n-1:
                personal_space = personal_space.union({pc1-11, pc1-10, pc1-9,
                                                       pc1-1, pc1, pc1+1,
                                                       pc1+9, pc1+10, pc1+11})
            elif pc1 % 10 == 0:
                personal_space = personal_space.union({pc1-10, pc1-9,
                                                       pc1, pc1+1,
                                                       pc1+10, pc1+11})
            else:
                personal_space = personal_space.union({pc1-11, pc1-10,
                                                       pc1-1, pc1,
                                                       pc1+9, pc1+10})
        for pc2 in assignedPositionsTuple2:
            if pc2 in personal_space:
                return False
        return True

    def __str__(self):
        return f"Destroyer Touching {ship2}"
        #return f"{kind_determiner(ship1)} Touching {kind_determiner(ship2)}"

    def __hash__(self):
        return self.hashnum


class CruiserPersonalSpace(Constraint):
    """SHIP1 = Submarine.
        Every ship pair(ship1 and ship2) do not
        invade another's personal space.
        i.e., every ship is surrounded by water at least one unit
        horizontally, vertically, diagonally."""
    def __init__(self, ship1: int, ship2: int):
        self.ship1 = ship1
        self.ship2 = ship2
        unique = "6"
        unique += str(ship1)
        unique += "101"
        unique += str(ship2)
        self.hashnum = int(unique)
        super().__init__({ship1, ship2})

    def valid_with_these_values(self, variable_to_value: dict, level):
        """Note, if ship1 is protected, ship2 is protected naturally.
        So we only need to check for one ship's personal space is protected."""
        # ship1, ship2 = self.variables_to_consider
        assignedOrientation1, assignedPositionsTuple1 = variable_to_value[
            self.ship1]
        assignedOrientation2, assignedPositionsTuple2 = variable_to_value[
            self.ship2]
        # HEAD personal space
        personal_space = set()
        for pc1 in assignedPositionsTuple1:
            if pc1 % 10 != 0 and pc1 % 10 != n-1:
                personal_space = personal_space.union({pc1-11, pc1-10, pc1-9,
                                                       pc1-1, pc1, pc1+1,
                                                       pc1+9, pc1+10, pc1+11})
            elif pc1 % 10 == 0:
                personal_space = personal_space.union({pc1-10, pc1-9,
                                                       pc1, pc1+1,
                                                       pc1+10, pc1+11})
            else:
                personal_space = personal_space.union({pc1-11, pc1-10,
                                                       pc1-1, pc1,
                                                       pc1+9, pc1+10})
        for pc2 in assignedPositionsTuple2:
            if pc2 in personal_space:
                return False
        return True

    def __str__(self):
        return f"Cruiser Touching {ship2}"
        # return f"{kind_determiner(ship1)} Touching {kind_determiner(ship2)}"

    def __hash__(self):
        return self.hashnum


class BattleshipPersonalSpace(Constraint):
    """SHIP1 = Submarine.
        Every ship pair(ship1 and ship2) do not
        invade another's personal space.
        i.e., every ship is surrounded by water at least one unit
        horizontally, vertically, diagonally."""
    def __init__(self, ship1: int, ship2: int):
        self.ship1 = ship1
        self.ship2 = ship2
        unique = "7"
        unique += str(ship1)
        unique += "101"
        unique += str(ship2)
        self.hashnum = int(unique)
        super().__init__({ship1, ship2})

    def valid_with_these_values(self, variable_to_value: dict, level):
        """Note, if ship1 is protected, ship2 is protected naturally.
        So we only need to check for one ship's personal space is protected."""
        # ship1, ship2 = self.variables_to_consider
        assignedOrientation1, assignedPositionsTuple1 = variable_to_value[
            self.ship1]
        assignedOrientation2, assignedPositionsTuple2 = variable_to_value[
            self.ship2]
        # HEAD personal space
        personal_space = set()
        for pc1 in assignedPositionsTuple1:
            if pc1 % 10 != 0 and pc1 % 10 != n-1:
                personal_space = personal_space.union({pc1-11, pc1-10, pc1-9,
                                                       pc1-1, pc1, pc1+1,
                                                       pc1+9, pc1+10, pc1+11})
            elif pc1 % 10 == 0:
                personal_space = personal_space.union({pc1-10, pc1-9,
                                                       pc1, pc1+1,
                                                       pc1+10, pc1+11})
            else:
                personal_space = personal_space.union({pc1-11, pc1-10,
                                                       pc1-1, pc1,
                                                       pc1+9, pc1+10})
        for pc2 in assignedPositionsTuple2:
            if pc2 in personal_space:
                return False
        return True

    def __str__(self):
        return f"Battleship Touching {ship2}"
        # return f"{kind_determiner(ship1)} Touching {kind_determiner(ship2)}"

    def __hash__(self):
        return self.hashnum

# ----------------------------------INPUT READING-------------------------------

for i in range(n):
    row_constraint[i] = int(string_row[i])
    col_constraint[i] = int(string_col[i])

ship_kind_num = {1: 0, 2: 0, 3: 0, 4: 0}
for i in range(0, len(string_ships)):
    ship_kind_num[i + 1] = int(string_ships[i])

for i in range(3, n+3):  # assume n+3==len(mylist)
    for j in range(n):
        content = mylist[i].rstrip()[j]
        pos = (i-3) * 10 + j
        if content == '0':
            continue
        elif content == 'W':
            preassigned[W].add(pos)

        elif content == 'S':
            preassigned[S].add(pos)
            if pos % 10 == n-1:
                aroundpreassigned[S] = aroundpreassigned[S].union({pos-11, pos-10,
                                                                   pos-1, pos,
                                                                   pos+9, pos+10})
            elif pos % 10 == 0:
                aroundpreassigned[S] = aroundpreassigned[S].union({pos-10, pos-9,
                                                                   pos, pos+1,
                                                                   pos+10, pos+11})
            else:
                aroundpreassigned[S] = aroundpreassigned[S].union({pos-11, pos-10, pos-9,
                                                                   pos-1, pos, pos+1,
                                                                   pos+9, pos+10, pos+11})

        elif content == 'L':
            preassigned[L].add(pos)
            if pos % 10 == n-1:
                aroundpreassigned[L] = aroundpreassigned[L].union({pos-11, pos-10,
                                                                   pos-1, pos,
                                                                   pos+9, pos+10})
            elif pos % 10 == 0:
                aroundpreassigned[L] = aroundpreassigned[L].union({pos-10, pos-9,
                                                                   pos, pos+1,
                                                                   pos+10, pos+11})
            else:
                aroundpreassigned[L] = aroundpreassigned[L].union({pos-11, pos-10, pos-9,
                                                                   pos-1, pos, pos+1,
                                                                   pos+9, pos+10, pos+11})

        elif content == 'T':
            preassigned[T].add(pos)
            if pos % 10 == n-1:
                aroundpreassigned[T] = aroundpreassigned[T].union({pos-11, pos-10,
                                                                   pos-1, pos,
                                                                   pos+9, pos+10})
            elif pos % 10 == 0:
                aroundpreassigned[T] = aroundpreassigned[T].union({pos-10, pos-9,
                                                                   pos, pos+1,
                                                                   pos+10, pos+11})
            else:
                aroundpreassigned[T] = aroundpreassigned[T].union({pos-11, pos-10, pos-9,
                                                                   pos-1, pos, pos+1,
                                                                   pos+9, pos+10, pos+11})

        elif content == 'R':
            preassigned[R].add(pos)
            if pos % 10 == n-1:
                aroundpreassigned[R] = aroundpreassigned[R].union({pos-11, pos-10,
                                                                   pos-1, pos,
                                                                   pos+9, pos+10})
            elif pos % 10 == 0:
                aroundpreassigned[R] = aroundpreassigned[R].union({pos-10, pos-9,
                                                                   pos, pos+1,
                                                                   pos+10, pos+11})
            else:
                aroundpreassigned[R] = aroundpreassigned[R].union({pos-11, pos-10, pos-9,
                                                                   pos-1, pos, pos+1,
                                                                   pos+9, pos+10, pos+11})

        elif content == 'B':
            preassigned[B].add(pos)
            if pos % 10 == n-1:
                aroundpreassigned[B] = aroundpreassigned[B].union({pos-11, pos-10,
                                                                   pos-1, pos,
                                                                   pos+9, pos+10})
            elif pos % 10 == 0:
                aroundpreassigned[B] = aroundpreassigned[B].union({pos-10, pos-9,
                                                                   pos, pos+1,
                                                                   pos+10, pos+11})
            else:
                aroundpreassigned[B] = aroundpreassigned[B].union({pos-11, pos-10, pos-9,
                                                                   pos-1, pos, pos+1,
                                                                   pos+9, pos+10, pos+11})

        else:  # middle part
            preassigned[M].add(pos)
            if pos % 10 == n-1:
                aroundpreassigned[M] = aroundpreassigned[M].union({pos-11, pos-10,
                                                                   pos-1, pos,
                                                                   pos+9, pos+10})
            elif pos % 10 == 0:
                aroundpreassigned[M] = aroundpreassigned[M].union({pos-10, pos-9,
                                                                   pos, pos+1,
                                                                   pos+10, pos+11})
            else:
                aroundpreassigned[M] = aroundpreassigned[M].union({pos-11, pos-10, pos-9,
                                                                   pos-1, pos, pos+1,
                                                                   pos+9, pos+10, pos+11})

# ---------------------- SUBMARINE -------------------
stack = []

for i in range(ship_kind_num[1]):
    creation = Submarine()
    unique = creation.hashnum
    rowC = SRowConstraint(unique)
    colC = SColConstraint(unique)
    creation.add_constraints_to_consider(hash(rowC))
    creation.add_constraints_to_consider(hash(colC))
    AllConstraints[hash(rowC)] = rowC
    AllConstraints[hash(colC)] = colC
    KINDtoHASH[1].add(unique)
    HASHtoKIND[unique] = 1
    HASHtoSHIP[unique] = creation
    ALL_HASHES.add(unique)
    stack.append(unique)

# assume preS_pos is done until stack ends(we have no more submarine).
for preS_pos in preassigned[S]:
    HASHtoSHIP[stack.pop()].add_possible_pos((0, (preS_pos,)))



# ------------------------------------------------------------------------------
# submarine 은 먼저 만들어져서, 얘네에 발도 못 붙이게 한다.


MoreShipPieceRevealed = {2: set(), 3: set(), 4:set()}
mutablepreassigned = deepcopy(preassigned)

for tpc in preassigned[T]:
    for bpc in preassigned[B]:
        if tpc + 10 == bpc:
            MoreShipPieceRevealed[2].add( (V, (tpc, bpc)) )
            mutablepreassigned[T].remove(tpc)
            mutablepreassigned[B].remove(bpc)

        elif tpc + 20 == bpc:
            MoreShipPieceRevealed[3].add( (V, (tpc, tpc+10, bpc)) )
            mutablepreassigned[T].remove(tpc)
            mutablepreassigned[B].remove(bpc)

        elif tpc + 30 == bpc:
            MoreShipPieceRevealed[4].add( (V, (tpc, tpc+10, tpc+20, bpc)) )
            mutablepreassigned[T].remove(tpc)
            mutablepreassigned[B].remove(bpc)

    for mpc in preassigned[M]:
        if tpc + 20 == mpc:
            MoreShipPieceRevealed[4].add( (V, (tpc, tpc+10, tpc+20, tpc+30)) )
            mutablepreassigned[T].remove(tpc)
            mutablepreassigned[M].remove(mpc)

for bpc in preassigned[B]:
    for mpc in preassigned[M]:
        if mpc + 20 == bpc:
            MoreShipPieceRevealed[4].add( (V, (bpc-30, bpc-20, bpc-10, bpc)) )
            mutablepreassigned[B].remove(bpc)
            mutablepreassigned[M].remove(mpc)







for lpc in preassigned[L]:
    for rpc in preassigned[R]:
        if lpc + 1 == rpc:
            MoreShipPieceRevealed[2].add( (H, (lpc, rpc)) )
            mutablepreassigned[L].remove(lpc)
            mutablepreassigned[R].remove(rpc)

        elif lpc + 2 == rpc:
            MoreShipPieceRevealed[3].add( (H, (lpc, lpc+1, rpc)) )
            mutablepreassigned[L].remove(lpc)
            mutablepreassigned[R].remove(rpc)

        elif lpc + 3 == rpc:
            MoreShipPieceRevealed[4].add( (H, (lpc, lpc+1, lpc+2, rpc)) )
            mutablepreassigned[L].remove(lpc)
            mutablepreassigned[R].remove(rpc)

    for mpc in preassigned[M]:
        if lpc + 2 ==  mpc:
            MoreShipPieceRevealed[4].add( (H, (lpc, lpc+1, lpc+2, lpc+3)) )
            mutablepreassigned[L].remove(lpc)
            mutablepreassigned[M].remove(mpc)

for rpc in preassigned[R]:
    for mpc in preassigned[M]:
        if mpc + 2 == rpc:
            MoreShipPieceRevealed[4].add( (H, (rpc-3, rpc-2, rpc-1, rpc)) )
            mutablepreassigned[R].remove(rpc)
            mutablepreassigned[M].remove(mpc)


# --------------------full ship이 주어졌다면, 이렇게 주어졌다.-------------------------
# 얘네는 오직 애네만 될 수 있다. # CannotbeCruiser, Cannotbebattleship, cannotbeBattleship
# 어라운드 시 케어 해줘야 됨. 호리전털일 떄.
# 무조건인 경우가 또 있다.

for a_given_piece in preassigned[L]:
    if a_given_piece % 10 == n-2:
        MoreShipPieceRevealed[2].add( (H, (a_given_piece, a_given_piece+1)) )
        mutablepreassigned[L].remove(a_given_piece)

for a_given_piece in preassigned[R]:
    if a_given_piece % 10 == 1:
        MoreShipPieceRevealed[2].add( (H, (a_given_piece-1, a_given_piece)) )
        mutablepreassigned[R].remove(a_given_piece)

for a_given_piece in preassigned[T]:
    if a_given_piece // 10 == n-2:
        MoreShipPieceRevealed[2].add( (V, (a_given_piece, a_given_piece+10)) )
        mutablepreassigned[T].remove(a_given_piece)

for a_given_piece in preassigned[B]:
    if a_given_piece // 10 == 1:
        MoreShipPieceRevealed[2].add( (V, (a_given_piece-10, a_given_piece)) )
        mutablepreassigned[B].remove(a_given_piece)

# 이때는 모두 무조건 디스트로이어이다.
#-----------------------------------------------------
# 배틀쉽은 절대 못 가는 프리어사인드도 있다. 이거는 나중에 크루저랑 디스트로이어만 보는 슏비인 컨스트레인트를 따로 만들어도 된다.

shouldbeinOneoftheDorC = set()
BattleshipCannotbeAround = set()

for a_given_piece in preassigned[L]:
    if a_given_piece % 10 == n-3:
        if a_given_piece + 1 in preassigned[M]:
            mutablepreassigned[L].remove(a_given_piece)
            mutablepreassigned[M].remove(a_given_piece+1)
            MoreShipPieceRevealed[3].add((H, (a_given_piece, a_given_piece+1, a_given_piece+2)))
        else:
            shouldbeinOneoftheDorC.add(a_given_piece)
            mutablepreassigned[L].remove(a_given_piece)
            # Lpc
            BattleshipCannotbeAround = \
                BattleshipCannotbeAround.union({a_given_piece-11, a_given_piece-10, a_given_piece-9,
                                                a_given_piece-1, a_given_piece, a_given_piece+1,
                                                a_given_piece+9, a_given_piece+10, a_given_piece+11})
            # Rpc
            a_given_piece = a_given_piece + 1
            BattleshipCannotbeAround = \
                BattleshipCannotbeAround.union({a_given_piece-11, a_given_piece-10, a_given_piece-9,
                                                a_given_piece-1, a_given_piece, a_given_piece+1,
                                                a_given_piece+9, a_given_piece+10, a_given_piece+11})

for a_given_piece in preassigned[R]:
    if a_given_piece % 10 == 2:
        if a_given_piece - 1 in preassigned[M]:
            mutablepreassigned[R].remove(a_given_piece)
            mutablepreassigned[M].remove(a_given_piece-1)
            MoreShipPieceRevealed[3].add((H, (a_given_piece-2, a_given_piece-1, a_given_piece)))
        else:
            shouldbeinOneoftheDorC.add(a_given_piece)
            mutablepreassigned[R].remove(a_given_piece)
            # Lpc
            BattleshipCannotbeAround = \
                BattleshipCannotbeAround.union({a_given_piece-11, a_given_piece-10, a_given_piece-9,
                                                a_given_piece-1, a_given_piece, a_given_piece+1,
                                                a_given_piece+9, a_given_piece+10, a_given_piece+11})
            # Rpc
            a_given_piece = a_given_piece - 1
            BattleshipCannotbeAround = \
                BattleshipCannotbeAround.union({a_given_piece-11, a_given_piece-10, a_given_piece-9,
                                                a_given_piece-1, a_given_piece, a_given_piece+1,
                                                a_given_piece+9, a_given_piece+10, a_given_piece+11})

for a_given_piece in preassigned[T]:
    if a_given_piece // 10 == n-3:
        if a_given_piece + 10 in preassigned[M]:
            mutablepreassigned[T].remove(a_given_piece)
            mutablepreassigned[M].remove(a_given_piece+10)
            MoreShipPieceRevealed[3].add((V, (a_given_piece, a_given_piece+10, a_given_piece+20)))
        else:
            shouldbeinOneoftheDorC.add(a_given_piece)
            mutablepreassigned[T].remove(a_given_piece)
            # Lpc
            if a_given_piece % 10 == n-1:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                           pos-1, pos,
                                                                           pos+9, pos+10})
            elif a_given_piece % 10 == 0:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                           pos, pos+1,
                                                                           pos+10, pos+11})
            else:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                           pos-1, pos, pos+1,
                                                                           pos+9, pos+10, pos+11})
            # Rpc
            a_given_piece = a_given_piece + 10
            if a_given_piece % 10 == n-1:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                           pos-1, pos,
                                                                           pos+9, pos+10})
            elif a_given_piece % 10 == 0:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                           pos, pos+1,
                                                                           pos+10, pos+11})
            else:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                           pos-1, pos, pos+1,
                                                                           pos+9, pos+10, pos+11})

for a_given_piece in preassigned[B]:
    if a_given_piece // 10 == 2:
        if a_given_piece - 10 in preassigned[M]:
            mutablepreassigned[B].remove(a_given_piece)
            mutablepreassigned[M].remove(a_given_piece-10)
            MoreShipPieceRevealed[3].add((V, (a_given_piece-20, a_given_piece-10, a_given_piece)))
        else:
            shouldbeinOneoftheDorC.add(a_given_piece)
            mutablepreassigned[B].remove(a_given_piece)
            # Lpc
            if a_given_piece % 10 == n-1:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                           pos-1, pos,
                                                                           pos+9, pos+10})
            elif a_given_piece % 10 == 0:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                           pos, pos+1,
                                                                           pos+10, pos+11})
            else:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                           pos-1, pos, pos+1,
                                                                           pos+9, pos+10, pos+11})
            # Rpc
            a_given_piece = a_given_piece - 10
            if a_given_piece % 10 == n-1:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                           pos-1, pos,
                                                                           pos+9, pos+10})
            elif a_given_piece % 10 == 0:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                           pos, pos+1,
                                                                           pos+10, pos+11})
            else:
                BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                           pos-1, pos, pos+1,
                                                                           pos+9, pos+10, pos+11})


# T_ODO: make a constraint just for a piece in shouldbeinOneoftheDorC
# ------------------------------------------------------------------------------
# more ship revealed는 이제 확정이니 그거 말고 다른 애들의 도메인에서는 제거해야되고, (1)
# 그거의 도메인에는 무조건 걔 하나만 갖는 애가 필요하다. (2) #TODO
SubmarineCannotBeAround = set()
DestroyerCannotBeAround = set()
CruiserCannotBeAround = set()
# (1)
for oriposs_pair in MoreShipPieceRevealed[2]:
    positions = oriposs_pair[1]
    for pos in positions:
        if pos % 10 == n-1:
            SubmarineCannotBeAround = SubmarineCannotBeAround.union({pos-11, pos-10,
                                                                     pos-1, pos,
                                                                     pos+9, pos+10})
            CruiserCannotBeAround = CruiserCannotBeAround.union({pos-11, pos-10,
                                                                 pos-1, pos,
                                                                 pos+9, pos+10})
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                       pos-1, pos,
                                                                       pos+9, pos+10})
        elif pos % 10 == 0:
            SubmarineCannotBeAround = SubmarineCannotBeAround.union({pos-10, pos-9,
                                                                     pos, pos+1,
                                                                     pos+10, pos+11})
            CruiserCannotBeAround = CruiserCannotBeAround.union({pos-10, pos-9,
                                                                 pos, pos+1,
                                                                 pos+10, pos+11})
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                       pos, pos+1,
                                                                       pos+10, pos+11})
        else:
            SubmarineCannotBeAround = SubmarineCannotBeAround.union({pos-11, pos-10, pos-9,
                                                                     pos-1, pos, pos+1,
                                                                     pos+9, pos+10, pos+11})
            CruiserCannotBeAround = CruiserCannotBeAround.union({pos-11, pos-10, pos-9,
                                                                 pos-1, pos, pos+1,
                                                                 pos+9, pos+10, pos+11})
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                       pos-1, pos, pos+1,
                                                                       pos+9, pos+10, pos+11})



for oriposs_pair in MoreShipPieceRevealed[3]:
    positions = oriposs_pair[1]
    for pos in positions:
        if pos % 10 == n-1:
            SubmarineCannotBeAround = SubmarineCannotBeAround.union({pos-11, pos-10,
                                                                     pos-1, pos,
                                                                     pos+9, pos+10})
            DestroyerCannotBeAround = DestroyerCannotBeAround.union({pos-11, pos-10,
                                                                     pos-1, pos,
                                                                     pos+9, pos+10})
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                       pos-1, pos,
                                                                       pos+9, pos+10})
        elif pos % 10 == 0:
            SubmarineCannotBeAround = SubmarineCannotBeAround.union({pos-10, pos-9,
                                                                     pos, pos+1,
                                                                     pos+10, pos+11})
            DestroyerCannotBeAround = DestroyerCannotBeAround.union({pos-10, pos-9,
                                                                     pos, pos+1,
                                                                     pos+10, pos+11})
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                       pos, pos+1,
                                                                       pos+10, pos+11})
        else:
            SubmarineCannotBeAround = SubmarineCannotBeAround.union({pos-11, pos-10, pos-9,
                                                                     pos-1, pos, pos+1,
                                                                     pos+9, pos+10, pos+11})
            DestroyerCannotBeAround = DestroyerCannotBeAround.union({pos-11, pos-10, pos-9,
                                                                     pos-1, pos, pos+1,
                                                                     pos+9, pos+10, pos+11})
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                       pos-1, pos, pos+1,
                                                                       pos+9, pos+10, pos+11})






# This is what happened:
# assume preS_pos is done until stack ends(we have no more submarine).
# for preS_pos in preassigned[S]:
#     HASHtoSHIP[stack.pop()].add_possible_pos((0, (preS_pos,)))

# remaining ship only
while len(stack) > 0:
    a_ship = HASHtoSHIP[stack.pop()]
    for i in range(n):
        if row_constraint[i] < 1:  # < 나의 호리전털 크기
            continue
        for j in range(n):
            if col_constraint[j] < 1:  # < 나의 호리전털 크기 왜냐 호리전털로 놓고 있어서
                continue
            pos = 10 * i + j
            if pos not in preassigned[W] and pos not in aroundpreassigned[L] and \
                    pos not in aroundpreassigned[B] and pos not in aroundpreassigned[T] \
                    and pos not in aroundpreassigned[B] and pos not in \
                    aroundpreassigned[M] and pos not in aroundpreassigned[S] \
                    and pos not in SubmarineCannotBeAround:
                a_ship.add_possible_pos( (0, (pos,)) )


# ------------------------------------------------------------------------------

for i in range(ship_kind_num[2]):
    creation = Destroyer()
    unique = creation.hashnum
    rowC = DRowConstraint(unique)
    colC = DColConstraint(unique)
    creation.add_constraints_to_consider(hash(rowC))
    creation.add_constraints_to_consider(hash(colC))
    AllConstraints[hash(rowC)] = rowC
    AllConstraints[hash(colC)] = colC
    KINDtoHASH[2].add(unique)
    HASHtoKIND[unique] = 2
    HASHtoSHIP[unique] = creation
    ALL_HASHES.add(unique)
    stack.append(unique)


for oriposs_pair in MoreShipPieceRevealed[2]:
    HASHtoSHIP[stack.pop()].add_possible_pos(oriposs_pair)
    positions = oriposs_pair[1]
    for pos in positions:
        if pos % 10 == n-1:
            DestroyerCannotBeAround = DestroyerCannotBeAround.union({pos-11, pos-10,
                                                                     pos-1, pos,
                                                                     pos+9, pos+10})
        elif pos % 10 == 0:
            DestroyerCannotBeAround = DestroyerCannotBeAround.union({pos-10, pos-9,
                                                                     pos, pos+1,
                                                                     pos+10, pos+11})
        else:
            DestroyerCannotBeAround = DestroyerCannotBeAround.union({pos-11, pos-10, pos-9,
                                                                     pos-1, pos, pos+1,
                                                                     pos+9, pos+10, pos+11})


while len(stack) > 0:
    a_ship = HASHtoSHIP[stack.pop()]
    # Finding possible head position
    # the num of middle+tail pieces that needs to be followed by the head
    num_middle_tail = (2 - 1)
    # here, num_middle_tail is 1, so destroyer needs
    # FOR HORIZONTAL:
    for i in range(n):
        if row_constraint[i] < 2:  # < H: longest side size V: one unit size
            continue
        for j in range(n - num_middle_tail):
            if col_constraint[j] < 1:  # < H: one unit size V: longest side size
                continue
            head = 10 * i + j
            tail = head + 1
            if head not in preassigned[W] and head not in aroundpreassigned[S] \
                    and head not in aroundpreassigned[M] and head not in DestroyerCannotBeAround:
                # because it is destroyer

                if tail not in preassigned[W] and tail not in \
                        aroundpreassigned[S] and tail not in aroundpreassigned[M] and tail not in DestroyerCannotBeAround:
                    # because it is destroyer

                    if head not in aroundpreassigned[T] and head not in \
                            aroundpreassigned[B] and head not in preassigned[R]:
                        # because it is HORIZONTAL and head

                        if tail not in aroundpreassigned[T] and tail not in \
                                aroundpreassigned[B] and tail not in \
                                preassigned[L]:
                            # because it is HORIZONTAL and tail

                            pair = (head, tail)
                            a_ship.add_possible_pos((H, pair))
    # FOR VERTICAL:
    for i in range(n - num_middle_tail):
        if row_constraint[i] < 1:  # < H: longest side size V: one unit size
            continue
        for j in range(n):
            if col_constraint[j] < 2:  # < H: one unit size V: longest side size
                continue
            head = 10 * i + j
            tail = head + 10
            if head not in preassigned[W] and head not in aroundpreassigned[S] \
                    and head not in aroundpreassigned[M] and head not in DestroyerCannotBeAround:
                # because it is destroyer

                if tail not in preassigned[W] and tail not in \
                        aroundpreassigned[S] and tail not in aroundpreassigned[M] \
                        and tail not in DestroyerCannotBeAround:
                    # because it is destroyer

                    if head not in aroundpreassigned[L] and head not in \
                            aroundpreassigned[R] and head not in preassigned[B]:
                        # because it is VERTICAL and head

                        if tail not in aroundpreassigned[L] and tail not in \
                                aroundpreassigned[R] and tail not in \
                                preassigned[T]:
                            # because it is VERTICAL and tail

                            pair = (head, tail)
                            a_ship.add_possible_pos((V, pair))
# ------------------------------------------------------------------------------

for i in range(ship_kind_num[3]):
    creation = Cruiser()
    unique = creation.hashnum
    rowC = CRowConstraint(unique)
    colC = CColConstraint(unique)
    creation.add_constraints_to_consider(hash(rowC))
    creation.add_constraints_to_consider(hash(colC))
    AllConstraints[hash(rowC)] = rowC
    AllConstraints[hash(colC)] = colC
    KINDtoHASH[3].add(unique)
    HASHtoKIND[unique] = 3
    HASHtoSHIP[unique] = creation
    ALL_HASHES.add(unique)
    stack.append(unique)


for oriposs_pair in MoreShipPieceRevealed[3]:
    HASHtoSHIP[stack.pop()].add_possible_pos(oriposs_pair)
    positions = oriposs_pair[1]
    for pos in positions:
        if pos % 10 == n-1:
            CruiserCannotBeAround = CruiserCannotBeAround.union({pos-11, pos-10,
                                                                 pos-1, pos,
                                                                 pos+9, pos+10})
        elif pos % 10 == 0:
            CruiserCannotBeAround = CruiserCannotBeAround.union({pos-10, pos-9,
                                                                 pos, pos+1,
                                                                 pos+10, pos+11})
        else:
            CruiserCannotBeAround = CruiserCannotBeAround.union({pos-11, pos-10, pos-9,
                                                                 pos-1, pos, pos+1,
                                                                 pos+9, pos+10, pos+11})


while len(stack) > 0:
    a_ship = HASHtoSHIP[stack.pop()]
    # Finding possible head position
    # the num of middle+tail pieces that needs to be followed by the head
    num_middle_tail = (3 - 1)
    # FOR HORIZONTAL:
    for i in range(n):
        if row_constraint[i] < 3:  # < H: longest side size V: one unit size
            continue
        for j in range(n - num_middle_tail):
            if col_constraint[j] < 1:  # < H: one unit size V: longest side size
                continue
            head = 10 * i + j
            middle = head + 1
            tail = head + 2
            if head not in preassigned[W] and head not in aroundpreassigned[S] and head not in CruiserCannotBeAround:
                if middle not in preassigned[W] and middle not in CruiserCannotBeAround: # and middle not in preassigned[S]:
                    if tail not in preassigned[W] and tail not in aroundpreassigned[S] and tail not in CruiserCannotBeAround:
                        # because it is cruiser

                        if head not in aroundpreassigned[T] and head not in \
                                aroundpreassigned[B] and head not in \
                                aroundpreassigned[R] and head not in \
                                preassigned[M]:
                            # because it is HORIZONTAL and head

                            if tail not in aroundpreassigned[T] and tail not in \
                                    aroundpreassigned[B] and tail not in \
                                    aroundpreassigned[L] and tail not in \
                                    preassigned[M]:
                                # because it is HORIZONTAL and tail
                                # cuz it's a middle piece
                                if middle not in aroundpreassigned[T] and middle not in \
                                        aroundpreassigned[B] and middle not in \
                                        preassigned[L] and middle not in \
                                        preassigned[R]:
                                    pair = (head, middle, tail)
                                    a_ship.add_possible_pos((H, pair))

    # FOR VERTICAL:
    for i in range(n - num_middle_tail):
        if row_constraint[i] < 1:  # < H: longest side size V: one unit size
            continue
        for j in range(n):
            if col_constraint[j] < 3:  # < H: one unit size V: longest side size
                continue
            head = 10 * i + j
            middle = head + 10
            tail = head + 20
            if head not in preassigned[W] and head not in aroundpreassigned[S] and head not in CruiserCannotBeAround:
                if middle not in preassigned[W] and middle not in CruiserCannotBeAround:
                    if tail not in preassigned[W] and tail not in aroundpreassigned[S] and tail not in CruiserCannotBeAround:
                        # because it is cruiser

                        if head not in aroundpreassigned[L] and head not in \
                                aroundpreassigned[R] and head not in \
                                aroundpreassigned[B] and head not in \
                                preassigned[M]:
                            # because it is VERTICAL and head

                            if tail not in aroundpreassigned[L] and tail not in \
                                    aroundpreassigned[R] and tail not in \
                                    aroundpreassigned[T] and tail not in \
                                    preassigned[M]:
                                # because it is VERTICAL and tail

                                if middle not in aroundpreassigned[T] and middle not in \
                                        aroundpreassigned[B] and middle not in \
                                        preassigned[L] and middle not in \
                                        preassigned[R]: # cuz it's a middle piece
                                    pair = (head, middle, tail)
                                    a_ship.add_possible_pos((V, pair))
# ------------------------------------------------------------------------------

for i in range(ship_kind_num[4]):
    creation = BattleShip()
    unique = creation.hashnum
    rowC = BRowConstraint(unique)
    colC = BColConstraint(unique)
    creation.add_constraints_to_consider(hash(rowC))
    creation.add_constraints_to_consider(hash(colC))
    AllConstraints[hash(rowC)] = rowC
    AllConstraints[hash(colC)] = colC
    KINDtoHASH[4].add(unique)
    HASHtoKIND[unique] = 4
    HASHtoSHIP[unique] = creation
    ALL_HASHES.add(unique)
    stack.append(unique)


for oriposs_pair in MoreShipPieceRevealed[4]:
    HASHtoSHIP[stack.pop()].add_possible_pos(oriposs_pair)
    positions = oriposs_pair[1]
    for pos in positions:
        if pos % 10 == n-1:
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10,
                                                                       pos-1, pos,
                                                                       pos+9, pos+10})
        elif pos % 10 == 0:
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-10, pos-9,
                                                                       pos, pos+1,
                                                                       pos+10, pos+11})
        else:
            BattleshipCannotbeAround = BattleshipCannotbeAround.union({pos-11, pos-10, pos-9,
                                                                       pos-1, pos, pos+1,
                                                                       pos+9, pos+10, pos+11})


while len(stack) > 0:
    a_ship = HASHtoSHIP[stack.pop()]
    # Finding possible head position
    # the num of middle+tail pieces that needs to be followed by the head
    num_middle_tail = (4 - 1)  # 고쳐
    # FOR HORIZONTAL:
    for i in range(n):
        if row_constraint[i] < 4:  # < H: longest side size V: one unit size
            continue
        for j in range(n - num_middle_tail):
            if col_constraint[j] < 1:  # < H: one unit size V: longest side size
                continue
            head = 10 * i + j
            m1 = head + 1
            m2 = head + 2
            tail = head + 3
            if head not in preassigned[W] and head not in aroundpreassigned[S] and head not in BattleshipCannotbeAround:
                if m1 not in preassigned[W] and m1 not in BattleshipCannotbeAround:
                    if m2 not in preassigned[W] and m2 not in BattleshipCannotbeAround:
                        if tail not in preassigned[W] and tail not in aroundpreassigned[S]:
                            # because it is cruiser

                            if head not in aroundpreassigned[T] and head not in \
                                    aroundpreassigned[B] and head not in \
                                    aroundpreassigned[R] and head not in \
                                    preassigned[M]:
                                # because it is HORIZONTAL and head

                                if tail not in aroundpreassigned[T] and tail not in \
                                        aroundpreassigned[B] and tail not in \
                                        aroundpreassigned[L] and tail not in \
                                        preassigned[M]:
                                    # because it is HORIZONTAL and tail

                                    if m1 not in preassigned[T] and m1 not in \
                                            preassigned[B] and m1 not in \
                                            preassigned[L] and m1 not in \
                                            preassigned[R]: # cuz it's a middle piece
                                        if m2 not in preassigned[T] and m2 not in \
                                                preassigned[B] and m2 not in \
                                                preassigned[L] and m2 not in \
                                                preassigned[R]: # cuz they are middle pieces

                                            pair = (head, m1, m2, tail)
                                            a_ship.add_possible_pos((H, pair))
    # FOR VERTICAL:
    for i in range(n - num_middle_tail):
        if row_constraint[i] < 1:  # < H: longest side size V: one unit size
            continue
        for j in range(n):
            if col_constraint[j] < 4:  # < H: one unit size V: longest side size
                continue
            head = 10 * i + j
            m1 = head + 10
            m2 = head + 20
            tail = head + 30
            if head not in preassigned[W] and head not in aroundpreassigned[S]:
                if m1 not in preassigned[W] and m1 not in preassigned[S]:
                    if m2 not in preassigned[W] and m2 not in \
                            preassigned[S] and tail not in preassigned[W] \
                            and tail not in aroundpreassigned[S]:
                        # because it is cruiser

                        if head not in aroundpreassigned[L] and head not in \
                                aroundpreassigned[R] and head not in \
                                aroundpreassigned[B] and head not in \
                                preassigned[M]:
                            # because it is VERTICAL and head

                            if tail not in aroundpreassigned[L] and tail not in \
                                    aroundpreassigned[R] and tail not in \
                                    aroundpreassigned[T] and tail not in \
                                    preassigned[M]:
                                # because it is VERTICAL and tail
                                # cuz it's a middle piece
                                if m1 not in preassigned[T] and m1 not in \
                                        preassigned[B] and m1 not in \
                                        preassigned[L] and m1 not in \
                                        preassigned[R] and m2 not in \
                                        preassigned[T] and m2 not in \
                                        preassigned[B] and m2 not in \
                                        preassigned[L] and m2 not in \
                                        preassigned[R]:
                                    pair = (head, m1, m2, tail)
                                    a_ship.add_possible_pos((V, pair))



# ------------------------------------------------------------------------------


# Pair making
hashes = list(ALL_HASHES)
for i in range(len(hashes)):
    for j in range(i+1, len(hashes)):
        ship1 = hashes[i]
        ship2 = hashes[j]
        if ship1 in KINDtoHASH[1]:
            creation = SubmarinePersonalSpace(ship1, ship2)
        if ship1 in KINDtoHASH[2]:
            creation = DestroyerPersonalSpace(ship1, ship2)
        if ship1 in KINDtoHASH[3]:
            creation = CruiserPersonalSpace(ship1, ship2)
        if ship1 in KINDtoHASH[4]:
            creation = BattleshipPersonalSpace(ship1, ship2)
        AllConstraints[creation.hashnum] = creation
        HASHtoSHIP[ship1].add_constraints_to_consider(creation.hashnum)
        HASHtoSHIP[ship2].add_constraints_to_consider(creation.hashnum)

for ats in mutablepreassigned[M]:
    creation = PreAssignedM(ats)
    AllConstraints[hash(creation)] = creation

for ats in mutablepreassigned[L]:
    creation = PreAssignedL(ats)
    AllConstraints[hash(creation)] = creation

for ats in mutablepreassigned[R]:
    creation = PreAssignedR(ats)
    AllConstraints[hash(creation)] = creation

for ats in mutablepreassigned[T]:
    creation = PreAssignedT(ats)
    AllConstraints[hash(creation)] = creation

for ats in mutablepreassigned[B]:
    creation = PreAssignedB(ats)
    AllConstraints[hash(creation)] = creation

for ats in shouldbeinOneoftheDorC:
    if ats in preassigned[M]:
        creation = PreAssignedM(ats)
    elif ats in preassigned[T]:
        creation = PreAssignedT(ats)
    elif ats in preassigned[B]:
        creation = PreAssignedB(ats)
    elif ats in preassigned[R]:
        creation = PreAssignedR(ats)
    elif ats in preassigned[L]:
        creation = PreAssignedL(ats)
    AllConstraints[hash(creation)] = creation

# --------------------FC Algorithm(FC check and FC algo)------------------------
def FCcheck(level: Level, C: int, X: int, assignment: dict):
    if len(level.CurDoms[X]) == 0:
        raise Exception(f"{X} doesn't have a domian")
    ConstraintC = AllConstraints[C]
    curdomx = copy(level.CurDoms[X])
    for d in curdomx:
        # if d == (0, (71,)):
        # print()
        if d not in level.CurDoms[X]:
            continue
        assignment[X] = d
        if not ConstraintC.valid_with_these_values(assignment, level):
            level.remove_d_from_T(X, d)
            # if d == (0, (94, 95, 96)):
            # print(f"{AllConstraints[C]} cutting {T}={d}")
            # print(f"{AllConstraints[C]} cutting {T}={d}")
    del(assignment[X])
    if len(level.CurDoms[X]) == 0:
        # print(f"DWO by {AllConstraints[C]}")
        return False
    return True

# 콜롬 딕셔너리 밖에서 써보자ㅜㅜ
#CurDomSaver = dict()
# depth = [0]
# KindTried = {1: set(), 2: set(), 3: set(), 4: set()}
KindTried = set()
Occupied = set()

def FC(level: Level, assigned: dict, unassigned: set):
    global KindTried
    if len(unassigned) == 0:
        return assigned
    Y = level.pick_unassigned_variable(unassigned)
    assigned[Y] = None
    unassigned = unassigned.difference(assigned) 
    TriedByMe = set()
    RowDictSaver = deepcopy(level.row_dict)  # 191 deep -> copy
    ColDictSaver = deepcopy(level.col_dict)  # 191 deep -> copy
    for d in level.CurDoms[Y]:
        if d[1] in KindTried:
            continue
        else:
            notoccupied = True
            for di in d[1]:
                global Occupied
                if di in Occupied:
                    notoccupied = False
                    break
            if notoccupied:
                KindTried.add(d[1])
                TriedByMe.add(d[1])
                Occupied = Occupied.union(d[1])
            else:
                continue
        
        CurDomSaver = deepcopy(level.CurDoms)

        assigned[Y] = d
        working = True
        for rowcolC in HASHtoSHIP[Y].constraints_to_consider:
            if rowcolC < 2600:
                if not AllConstraints[rowcolC].valid_with_these_values(assigned, level):
                    working = False
                    KindTried.remove(d[1])
                    Occupied = Occupied.difference(d[1])
                    level.row_dict = deepcopy(RowDictSaver)
                    level.col_dict = deepcopy(ColDictSaver)
                    break
        if not working:
            continue

        theresway = True
        for unv in unassigned:
            for dis in copy(level.CurDoms[unv]):
                for dd in d[1]:
                    if dd in dis[1] and dis[1] in level.CurDoms[unv]:
                        level.remove_d_from_T(unv, dis)
                        if 0 == len(level.CurDoms[unv]):
                            level.CurDoms = CurDomSaver  # 191 copy ->> no
                            level.row_dict = RowDictSaver  # 191 copy ->> no
                            level.col_dict = ColDictSaver  # 191 copy ->> no
                            Occupied = Occupied.difference(d[1])
                            theresway = False
                            break
            if not theresway:
                break
        if not theresway:
            continue

        DWOhappened = False
        for C in HASHtoSHIP[Y].constraints_to_consider:
            variable_missed_count = 0
            for variable in AllConstraints[C].variables_to_consider:
                if variable not in assigned:
                    variable_missed_count += 1
                    X = variable
            if variable_missed_count == 1:
                if not FCcheck(level, C, X, assigned):
                    level.row_dict = deepcopy(RowDictSaver)
                    level.col_dict = deepcopy(ColDictSaver)
                    DWOhappened = True
                    break
        if not DWOhappened:
            # depth[0] += 1
            a = FC(Level(level.row_dict, level.col_dict, level.CurDoms), assigned, unassigned)
            if a is not None:
                # print(level.col_dict)
                return a
            else:
                # if Y == 1:
                #     print()
                level.CurDoms = CurDomSaver  # 191 copy ->> no
                level.row_dict = deepcopy(RowDictSaver)
                level.col_dict = deepcopy(ColDictSaver)
                # KindTried.remove(d[1])  # 292에 있던 애들을 여기로
                Occupied = Occupied.difference(d[1])
                # print(f"ok so {d} didn't work.")
                continue

                # depth[0] -= 1
        else:
            level.CurDoms = deepcopy(CurDomSaver)  # 191 copy ->> no
            level.row_dict = deepcopy(RowDictSaver)  # 191 copy ->> no
            level.col_dict = deepcopy(ColDictSaver)  # 191 copy ->> no
            # KindTried.remove(d[1])
            Occupied = Occupied.difference(d[1])
    del(assigned[Y])
    unassigned.add(Y)
    KindTried = KindTried.difference(TriedByMe)
    return None


# -------------------------SOLVING AND WRITING----------------------------------

initial_level = Level(row_dict=copy(row_constraint), col_dict=copy(col_constraint))
solution = FC(initial_level, {}, copy(ALL_HASHES))
# test = FC(initial_level, {1: (0, (37,)), 2: (0, (55,)), 3: (0, (69,)), 4: (0, (70,)), 5: (1, (40, 50)), 6: (1, (88, 98)), 7: (0, (91, 92)), 8: (0, (10, 11, 12)), 9: (0, (94, 95, 96)), 10: (1, (42, 52, 62, 72))}, set())
if solution is None:
    print("I am very sorry, I couldn't find a solution.")
    exit()
else:
    print(solution)


def convert_positions(positions101: int) -> tuple:
    return positions101 // 10, positions101 % 10


def draw_ship(orientation: int, positions: tuple) -> dict:
    if len(positions) == 1:
        return {convert_positions(positions[0]): 'S'}
    if orientation == H:
        head = 'L'
        tail = 'R'
    else:
        head = 'T'
        tail = 'B'
    head_tail_only = {convert_positions(positions[0]): head, convert_positions(positions[-1]): tail}
    for remaining_pos in positions[1:-1]:
        head_tail_only[convert_positions(remaining_pos)] = 'M'
    return head_tail_only


lis = []
sublis = ['W'] * n
for i in range(n):
    lis.append(copy(sublis))

for variable_hash in solution:
    orientation, positions = solution[variable_hash]
    should_draw = draw_ship(orientation, positions)
    for i, j in should_draw:
        lis[i][j] = should_draw[(i,j)]

flattened = [item for sublist in lis for item in sublist]

lisToString = ""
for chunk in [''.join(flattened[i:i + n]+['\n']) for i in range(0, n*n, n)]:
    lisToString += chunk

with open(output_filename, 'w') as output_file:
    # write the outputs in exact format
    output_file.writelines(lisToString.rstrip())
    # slicing to get rid of the last new line.
