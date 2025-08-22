import type { KeyData } from "../types";

interface ProfileProps {
  response: KeyData | null;
  callEndpoint: (endpoint: string, method: string, data?: any) => Promise<any>;
}

const Profile = ({ response, callEndpoint }: ProfileProps) => {
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <h2 className="text-xl font-bold mb-4">Profile</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <button
            onClick={() => callEndpoint("public-key", "GET")}
            className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center mb-4"
          >
            <span className="material-symbols-outlined mr-1">key</span>
            Get Public Key
          </button>
          {response?.public_key && (
            <div className="bg-gray-700/50 p-4 rounded-lg">
              <p className="text-sm break-all">{response.public_key}</p>
            </div>
          )}
        </div>
        <div>
          <button
            onClick={() => callEndpoint("public-private-key", "GET")}
            className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center mb-4"
          >
            <span className="material-symbols-outlined mr-1">lock</span>
            Get Private Key
          </button>
          {response?.private_key && (
            <div className="bg-gray-700/50 p-4 rounded-lg">
              <p className="text-sm break-all">{response.private_key}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
