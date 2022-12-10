from typing import Tuple, List, Optional, Union

ListResults = Tuple[List, Optional[Exception]]
RemoveResults = Tuple[bool, Optional[Exception]]
FilterResults = Tuple[Union[bool, str], Optional[Exception]]
