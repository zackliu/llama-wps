﻿using LLama.Abstractions;
using LLama.Common;
using LLama.Web.Common;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Threading.Tasks;

namespace LLama.Web.Services
{

    /// <summary>
    /// Sercive for handling Models,Weights & Contexts
    /// </summary>
    public class ModelService : IModelService
    {
        private readonly LLamaOptions _configuration;
        private readonly ILogger<ModelService> _llamaLogger;
        private readonly ILLamaExecutor _executor;

        /// <summary>
        /// Initializes a new instance of the <see cref="ModelService"/> class.
        /// </summary>
        /// <param name="logger">The logger.</param>
        /// <param name="options">The options.</param>
        public ModelService(IOptions<LLamaOptions> configuration, ILogger<ModelService> llamaLogger)
        {
            _llamaLogger = llamaLogger;
            _configuration = configuration.Value;

            var parameters = new ModelParams(_configuration.Models.ModelPath)
            {
                ContextSize = 2048,
                Seed = 1337,
                GpuLayerCount = 6,
                Threads = 16
            };
            var model = LLamaWeights.LoadFromFile(parameters);
            var context = model.CreateContext(parameters);
            _executor = new InteractiveExecutor(context);
        }

        public ILLamaExecutor GetExecutor()
        {
            return _executor;
        }
    }
}
