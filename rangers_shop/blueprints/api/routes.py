from flask import Blueprint, request, jsonify 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from rangers_shop.models import db, Customer, ProdOrder, Order,  Product, product_schema, product_schemas


api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/token', methods = ['GET', 'POST'])
def token():

    data = request.json
    if data: 
        client_id = request.json['client_id']
        access_token = create_access_token(identity=client_id)
        return {
            'status': 200,
            'access_token': access_token
        }
    else:
        return {
            'status': 400,
            'message': 'Missing Client Id. Try Again'
        }


@api.route('/shop')
@jwt_required()
def get_shop():

    shop = Product.query.all()

    response = product_schemas.dump(shop)
    return jsonify(response)


@api.route('/order/<cust_id>', methods = ['GET'])
@jwt_required()
def get_orders(cust_id):
    

    #need to grab all the orders made by each customer, and all the products associated with each order 
    #first grab all the diferent order_ids for uses
    #then grab the individual products per the orders 

    prodord = ProdOrder.query.filter(ProdOrder.cust_id == cust_id).all()

    # data = {}
    data = []
    # id = 1

    #we need to traverse the prodord to get all the individual orders for that customer
    for order in prodord:

        # if order.order_id not in data:
        #     data[order.order_id] = []

        print(order.quantity)
            
        #query the Product object associated with the product_id 
        product = Product.query.filter(Product.prod_id == order.prod_id).first()

        #use our schema to jsonify our product &
        prod_data = product_schema.dump(product)
    
        #for the product quantity on order not the total quantity available 
        prod_data['quantity'] = order.quantity
        prod_data['order_id'] = order.order_id
        prod_data['id'] = order.prodord_id
        # id += 1

        #add quantity attribute to that product before putting it in our list
        # product.quantity = order.quantity
        # data[order.order_id].append(prod_data)
        data.append(prod_data)



    return data 




@api.route('/order/<cust_id>', methods = ['POST'])
@jwt_required()
def create_order(cust_id):
    data = request.json
    print(data)

    cust_order  = data['order']

    customer = Customer.query.filter(Customer.cust_id == cust_id).first()
    if not customer:
        customer = Customer(cust_id)
        db.session.add(customer)


    order = Order()
    db.session.add(order)

    for product in cust_order:
        print(product)
        prodord = ProdOrder(product['prod_id'], product['quantity'], product['price'], order.order_id, customer.cust_id)
        db.session.add(prodord)

        #adds price from prodord (which multiples quantity by price) to order total
        order.increment_order_total(prodord.price)

        #decrements total quantity of product when bought by customer 
        current_product = Product.query.get(product['prod_id'])
        current_product.decrement_quantity(product['quantity'])

    db.session.commit()

    return {
        'status': 200,
        'message': 'new order was created!'
    }


@api.route('/order/<order_id>', methods = ['PUT'])
@jwt_required()
def update_order(order_id):

    data = request.json
    new_quantity = int(data['quantity'])
    prod_id = data['prod_id']

    print(prod_id)
    print(new_quantity)
    


    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()
    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)


    #sets the new quantity of that product for this specific order and the total cost of that product for the order
    
    
    prodorder.set_price(product.price, new_quantity)

    diff = abs(new_quantity - prodorder.quantity)
    print("diff", diff)

    #if our new quantity is less than the old, we can add back to our product quantity & decrement our order $ total
    if prodorder.quantity > new_quantity:
        product.increment_quantity(diff)
        order.decrement_order_total(prodorder.price)

    #if our new quantity is more than the old, we need to take away product quantity & incrmeent our order $ total
    elif prodorder.quantity < new_quantity:
        product.decrement_quantity(diff)
        order.increment_order_total(prodorder.price)

    prodorder.update_quantity(new_quantity)

    db.session.commit()

    return {
        'status': 200,
        'message': 'order was updated!'
    }



@api.route('/order/<order_id>', methods = ['DELETE'])
@jwt_required()
def delete_item_order(order_id):

    
    data = request.json
    print('data', data)
    prod_id = data['prod_id']
    # print(prod_id)
    # print(order_id)

    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()
    # print(prodorder)
    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)

    # print(order)
    # print(prodorder.price)
    order.decrement_order_total(prodorder.price)
    product.increment_quantity(prodorder.quantity)

    

    db.session.delete(prodorder)
    db.session.commit()


    return {
        'status': 200,
        'message': 'order was deleted!'
    } 