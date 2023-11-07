from enum import Enum
import ctypes
import json
import platform
import os
from typing import Union, Any

class Product(Enum):
    CombatRecord_0 = 0
    CombatRecord_1 = 1
    CombatRecord_2 = 2
    Gold = 3
    OriginFragment_0 = 4
    OriginFragment_1 = 5

class Facility(Enum):
    ControlCenter = 0
    Office = 1
    Reception = 2
    Training = 3
    Crafting = 4
    Dormitory_1 = 5
    Dormitory_2 = 6
    Dormitory_3 = 7
    Dormitory_4 = 8
    B101 = 9
    B102 = 10
    B103 = 11
    B201 = 12
    B202 = 13
    B203 = 14
    B301 = 15
    B302 = 16
    B303 = 17

class Simulator:
    _loaded = False
    
    def __init__(self, json_data: Union[str, Any] = None) -> None:
        if not Simulator._loaded:
            raise Exception("InfrastSim 动态库未加载")
        
        if json_data is not None:
            json_data = Simulator._ensure_utf8_json(json_data)
            self._id = Simulator.__lib.CreateSimulatorWithData(json_data, 1)
        else:
            self._id = Simulator.__lib.CreateSimulator()

    def __del__(self) -> None:
        Simulator.__lib.DestroySimulator(self._id)

    def get_data(self, detailed: bool = True) -> any:
        result = Simulator.__lib.GetData(self._id, int(detailed))
        return json.loads(result)

    def simulate(self, seconds: int) -> None:
        Simulator.__lib.Simulate(self._id, seconds)

    def set_facility_state(self, facility: Facility | int, json_data: Union[str, Any]) -> None:
        json_data = Simulator._ensure_utf8_json(json_data)
        Simulator.__lib.SetFacilityState(self._id, Simulator._fac2int(facility), json_data)

    def set_upgraded(self, json_data: Union[str, Any]) -> None:
        json_data = Simulator._ensure_utf8_json(json_data)
        Simulator.__lib.SetUpgraded(self._id, json_data)

    def set_level(self, facility: Facility | int, level: int) -> None:
        Simulator.__lib.SetLevel(self._id, Simulator._fac2int(facility), level)

    def set_strategy(self, facility: Facility | int, strategy: int) -> None:
        Simulator.__lib.SetStrategy(self._id, Simulator._fac2int(facility), strategy)

    def set_product(self, facility: Facility | int, product: Product) -> None:
        Simulator.__lib.SetProduct(self._id, Simulator._fac2int(facility), product.value)

    def remove_operator(self, facility: Facility | int, idx: int) -> None:
        Simulator.__lib.RemoveOperator(self._id, Simulator._fac2int(facility), idx)

    def remove_operators(self, facility: Facility | int) -> None:
        Simulator.__lib.RemoveOperators(self._id, Simulator._fac2int(facility))

    def collect_all(self) -> None:
        Simulator.__lib.CollectAll(self._id)

    def collect(self, facility: Facility | int, idx: int = 0) -> None:
        Simulator.__lib.Collect(self._id, Simulator._fac2int(facility), idx)

    def use_drones(self, facility: Facility | int, amount: int) -> int:
        return Simulator.__lib.UseDrones(self._id, Simulator._fac2int(facility), amount)

    def sanity(self, amount: int) -> None:
        Simulator.__lib.Sanity(self._id, amount)

    def get_data_for_mower(self) -> any:
        result = Simulator.__lib.GetDataForMower(self._id)
        return json.loads(result)

    @staticmethod
    def enumerate_group(data) -> any:
        data = Simulator._ensure_utf8_json(data)
        result = Simulator.__lib.EnumerateGroup(data)
        return json.loads(result)

    @staticmethod
    def _ensure_utf8_json(data: Union[str, Any]) -> str:
        """Ensure the provided data is a JSON string."""
        return data.encode('utf-8') if isinstance(data, str) else json.dumps(data).encode('utf-8')
    
    @staticmethod
    def _fac2int(fac: Facility | int)->int:
        return fac if isinstance(fac, int) else fac.value
    
    @staticmethod
    def load(dll_path = None):
        if Simulator._loaded:
            raise Exception("动态库已经加载")
            
        system = platform.system()
        if not dll_path or os.path.isdir(dll_path):
            if system == "Windows":
                surfix = ".dll"
            elif system == "Darwin":  # macOS
                surfix = ".dylib"
            elif system == "Linux":
                surfix =  ".so"
            else:
                raise EnvironmentError(f"Unsupported operating system: {system}")
            if not dll_path:
                dll_path = os.path.abspath(f'./InfrastSim{surfix}')
            else:
                dll_path = os.path.join(dll_path, f'InfrastSim{surfix}')

        Simulator.__lib = ctypes.CDLL(dll_path)
        Simulator.__set_lib_properties()
        Simulator._loaded = True

    @staticmethod
    def __set_lib_properties():
        Simulator.__lib.GetData.restype = ctypes.c_char_p
        Simulator.__lib.GetDataForMower.restype = ctypes.c_char_p
        Simulator.__lib.EnumerateGroup.restype = ctypes.c_char_p

if __name__ == '__main__':
    Simulator.load()
    sim = Simulator()
    with open('out.json', 'w+') as f:
        f.write(sim.get_data())