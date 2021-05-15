



from flask import request, current_app
from app import db
from app.inventory import bp
from app.auth.auth import token_auth
from app.models import Inventory
from app.errors.errors import bad_request


# create inventory
@bp.route('inventory', methods=['POST'])
@token_auth.login_required
def create_inventory():
    data = request.get_json() or {}

    #mand_fields = ('name')
    #if not all(field in data for field in mand_fields):
    if 'name' not in data:
        return bad_request('Please provide all mandatory fields')

    inventory = Inventory()
    inventory.from_dict(data, update_by=token_auth.current_user().email)
    db.session.add(inventory)
    db.session.commit()

    return inventory.to_dict()


# update inventory
@bp.route('inventory/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    data = request.get_json() or {}

    if data:
        inventory.from_dict(data, update_by=token_auth.current_user().email)
        db.session.add(inventory)
        db.session.commit()

    return inventory.to_dict()


# delete inventory
@bp.route('inventory/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_inventory():
    inventory = Inventory.query.get_or_404(id)
    db.session.delete(inventory)
    db.session.commit()

    return {'message': 'inventory deleted'}


# get one inventory
@bp.route('inventory/<int:id>', methods=['GET'])
@token_auth.login_required
def get_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    
    return inventory.to_dict()


# get all inventory
@bp.route('inventory', methods=['GET'])
@token_auth.login_required
def get_all_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get(
        'per_page', current_app.config['PAGINATION_MIN'], type=int),
        current_app.config['PAGINATION_MAX'])
    curr_user = token_auth.current_user()
    data = Inventory.to_collection_dict(
        Inventory.query, page, per_page, 'inventory.get_all_inventory')

    return data

