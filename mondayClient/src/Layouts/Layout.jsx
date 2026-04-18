import { useNavigate, Outlet, useLocation } from "react-router-dom";

function Layout() {
    const navigate = useNavigate();
    const location = useLocation();

    const handleBack = () => {
        if (window.history.length > 1) {
            navigate(-1);
        } else {
            navigate("/");
        }
    };

    const isHome = location.pathname === "/";

    return (
        <div className="min-h-screen bg-gray-50">

            {/* Top Bar */}
            <div className="bg-white border-b px-4 py-3 flex items-center">
                
                {!isHome && (
                    <button
                        onClick={handleBack}
                        className="text-gray-600 hover:text-gray-900"
                    >
                        ← Back
                    </button>
                )}

                <h1 className="ml-4 font-semibold">Monday</h1>
            </div>

            {/* Page Content */}
            <Outlet />

        </div>
    );
}

export default Layout;