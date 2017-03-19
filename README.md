# neitris

## requirements

* python 2
* pygame

## installation

* `pip install pygame`
* `cp neitris_cfg.py.example neitris_cfg.py`

## configuration
|        key        |  value  |                     description                     |
|-------------------|---------|-----------------------------------------------------|
| MAXLEVEL          | 7       | maximum level speed                                 |
| GENERATE_POWERUPS | 0       | enable/disable fancy powerups                       |
| SHOW_GRID         | 1       | enable/disable helping lines                        |
| THEME             | neitris | use specified theme from ./theme directory          |
| SCALE_FACTOR      | 1       | scales all items by given factor (useful for HIDPI) |


## run

* `python neitris_server.py`
* `python neitris.py [HOST]`
