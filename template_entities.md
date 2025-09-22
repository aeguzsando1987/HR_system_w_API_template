## Example Entities



## Example Entity
### Campos
- code: str
- title: str
- description: str

## Person Entity
### Campos
- id: int
- name: str
- last_name: str
- email: str
- phone: str
- address: str
- user_id: int (FK relacionada con User Entity)
- created_at: datetime
- updated_at: datetime
- deleted_at: datetime
- updated_by: int (FK relacionada con User Entity)
- status: str
- is_deleted:bool
