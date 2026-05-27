import { Product } from "../lib/api";

type Props = {
  products: Product[];
};

export function DataTable({ products }: Props) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Product</th>
            <th>Category</th>
            <th>Supplier</th>
            <th>On hand</th>
            <th>Margin</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => {
            const margin = ((product.unit_price - product.unit_cost) / product.unit_price) * 100;
            return (
              <tr key={product.id}>
                <td>{product.sku}</td>
                <td>{product.name}</td>
                <td>{product.category_name}</td>
                <td>{product.supplier_name}</td>
                <td>
                  <span className={product.quantity_on_hand <= product.reorder_point ? "pill danger" : "pill"}>
                    {product.quantity_on_hand}
                  </span>
                </td>
                <td>{margin.toFixed(1)}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
