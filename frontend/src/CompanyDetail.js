import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, BarChart, Bar, Legend,
} from "recharts";
import "./App.css";

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
};

export default function CompanyDetail() {
  const { companyName } = useParams();
  const [company, setCompany] = useState(null);
  const [financeData, setFinanceData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        const detailsResponse = await fetch(`http://localhost:5001/api/company/${encodeURIComponent(companyName)}`);
        if (!detailsResponse.ok) throw new Error("Company details not found");
        const detailsData = await detailsResponse.json();
        setCompany(detailsData);

        const financeResponse = await fetch(`http://localhost:5001/api/company/${encodeURIComponent(detailsData.name)}/finance`);
        if (financeResponse.ok) {
          const finData = await financeResponse.json();
          setFinanceData(finData);
        } else {
          setFinanceData(null);
        }
      } catch (error) {
        console.error("Failed to fetch data:", error);
        setCompany(null);
      } finally {
        setLoading(false);
      }
    };
    fetchAllData();
  }, [companyName]);

  if (loading) {
    return <div className="detail-container"><h2>Loading...</h2></div>;
  }

  if (!company) {
    return <div className="detail-container"><h2>Company Not Found</h2><Link to="/" className="cta-link back-button">← Back to Search</Link></div>;
  }

  const beforeStockData = financeData?.before_stock_data.map(item => ({ ...item, Date: formatDate(item.Date) })) || [];
  const afterStockData = financeData?.after_stock_data.map(item => ({ ...item, Date: formatDate(item.Date) })) || [];
  const revenueData = financeData?.revenue_data.map(item => ({ ...item, Date: formatDate(item.Date) })) || [];

  return (
    <div className="page-container">
      <div className="detail-container">
        <Link to="/" className="cta-link back-button">← Back to Search</Link>
        <h1 className="company-detail-name">{company.name}</h1>
        <p className="company-detail-summary">{company.description}</p>
        <p className="company-detail-date">Event Date: {company.month} {company.year}</p>
        {company.link && <a href={company.link} target="_blank" rel="noopener noreferrer" className="cta-link">Visit Source: {company.source || 'Official Site'}</a>}

        {financeData ? (
          <div className="charts-container">
            {/* Stock Price Charts */}
            <div className="chart-row">
              <div className="chart-block">
                <h3 className="chart-title">Stock Price: 6 Months Before Event</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={beforeStockData}>
                    <CartesianGrid stroke="#ccc" strokeDasharray="3 3" />
                    <XAxis dataKey="Date" />
                    <YAxis domain={['dataMin', 'dataMax']} />
                    <Tooltip />
                    <Line type="monotone" dataKey="Close" stroke="#8884d8" name="Price" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
                <p className="insight-text">Overall Trend (Before): <span className={`trend-${financeData.before_trend}`}>{financeData.before_trend}</span></p>
              </div>
              <div className="chart-block">
                <h3 className="chart-title">Stock Price: 6 Months After Event</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={afterStockData}>
                    <CartesianGrid stroke="#ccc" strokeDasharray="3 3" />
                    <XAxis dataKey="Date" />
                    <YAxis domain={['dataMin', 'dataMax']} />
                    <Tooltip />
                    <Line type="monotone" dataKey="Close" stroke="#82ca9d" name="Price" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
                <p className="insight-text">Overall Trend (After): <span className={`trend-${financeData.after_trend}`}>{financeData.after_trend}</span></p>
              </div>
            </div>

            {/* Revenue Chart */}
            <div className="chart-row">
                <div className="chart-block full-width">
                    <h3 className="chart-title">Quarterly Revenue</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={revenueData}>
                            <CartesianGrid stroke="#ccc" strokeDasharray="3 3" />
                            <XAxis dataKey="Date" />
                            <YAxis />
                            <Tooltip formatter={(value) => new Intl.NumberFormat('en-US', { notation: 'compact', compactDisplay: 'short' }).format(value)} />
                            <Legend />
                            <Bar dataKey="Revenue" fill="#ffc658" name="Total Revenue" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
          </div>
        ) : (
          <div className="charts-container">
            <p>Financial data is not available for this company.</p>
          </div>
        )}
      </div>
    </div>
  );
}
